import codecs
import datetime
import json
import logging
import os
import threading
import urllib.request

import slowfit.util

from ..models.base import Country, RegisteredClasses
from ..models.base import BikeType
from ..models.base import Material
from ..models.bikes import Brand
from ..models.bikes import Frame
from ..models.bikes import FrameSize
from ..models.imports import ImportLog, START, BUSY, ERRORS, OK


logger = logging.getLogger(__name__)


class JSONImportSession(threading.Thread):
	def __init__(self, user, folder):
		super(JSONImportSession, self).__init__()
		self.user = user
		self.log = None
		self.folder = folder
		self.brand = None
		self.sync = True
		self._action = None
		self._directory = []

	def log_error(self, fmt, *args):
		self.log.log_error(fmt, *args)

	def set_status(self, status):
		self.log.set_status(status)

	class ReferenceObjectDoesNotExist(Exception):
		def __init__(self, entity, model, key, field):
			self.message = f"{entity}: no {model.__name__} with {field} '{key}' found"

		def __str__(self):
			return self.message

	class ReferenceObjectNotUnique(Exception):
		def __init__(self, entity, model, key, field):
			self.message = f"{entity}: {model.__name__} with {field} '{key}' not unique"

		def __str__(self):
			return self.message

	@staticmethod
	def get_reference(entity, model, key, foreign_field="name"):
		objects = model.objects.filter(**{foreign_field: key})
		if not objects:
			raise JSONImportSession.ReferenceObjectDoesNotExist(entity, model, key, foreign_field)
		elif len(objects) > 1:
			raise JSONImportSession.ReferenceObjectNotUnique(entity, model, key, foreign_field)
		else:
			return objects[0]

	def _import_session(self, action):
		try:
			self.log = ImportLog()
			self.log.importedBy = self.user
			self.log.reference = self.folder
			self.set_status(START)

			self._action = action
			if self.sync:
				self.run()
			else:
				self.start()
		except Exception as e:
			logger.exception("Exception caught: ", exc_info=e)
			self.log_error(str(e))

	def run(self):
		try:
			datestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
			self.log.title = f"{self.folder} {datestr}"
			self.set_status(BUSY)

			self._action()

			if self.log.status != ERRORS:
				self.set_status(OK)

		except Exception as e:
			logger.exception("Exception caught: ", exc_info=e)
			self.log_error(str(e))

	def import_data(self):
		def _scan_folder():
			with os.scandir(self.folder) as it:
				for entry in it:
					if entry.is_file() and entry.name.endswith(".json"):
						with codecs.open(entry, 'r', 'utf-8') as fh:
							self.import_model(json.load(fh), entry.name.split(".")[0])

			with os.scandir(self.folder) as it:
				for entry in it:
					if entry.is_dir():
						self.import_bike_data(entry)

		self._import_session(_scan_folder)

	def import_brand(self, brand):
		def _find_folder():
			with os.scandir(self.folder) as it:
				for entry in it:
					if entry.is_dir() and brand == entry.name:
						self.import_bike_data(entry)
		self._import_session(_find_folder)

	def import_model_data(self, model_name):
		def _import_model():
			with codecs.open(os.path.join(self.folder, model_name + ".json"), 'r', 'utf-8') as fh:
				data = json.load(fh)
				self.import_model(model_name, data)
		self._import_session(_import_model)

	def import_all_model_data(self):
		def _import_all_models():
			with os.scandir(self.folder) as it:
				for entry in it:
					if entry.is_file() and entry.name.endswith(".json"):
						with codecs.open(entry, 'r', 'utf-8') as fh:
							self.import_model(entry.name.split(".")[0], json.load(fh))
		self._import_session(_import_all_models)

	def import_model(self, model_name, model_data):
		model = RegisteredClasses.get_class(model_name)
		if model is None:
			return
		defaults = model_data.get("_defaults", {})
		for key, values in model_data.items():
			if key != "_defaults":
				args = {"defaults": defaults, "name": key}
				args.update(values)
				try:
					model.objects.get_or_create(**args)
				except Exception as e:
					self.log_error("Exception importing '{0}' '{1}': {2}", model_name, key, e)

	def make_brand(self, directory):
		self._directory.append(directory)
		try:
			try:
				with codecs.open(os.path.join(directory, directory.name + ".json"), 'r', 'utf-8') as fh:
					data = json.load(fh)
			except FileNotFoundError:
				data = {}

			country_code: str = data.get("country")
			if country_code:
				data["country"] = self.get_reference(directory.name, Country, country_code.upper(), "isoCode")
			assets = data.pop("assets", None)
			notes = data.pop("notes", None)

			logger.info("Importing Brand '%s'", directory.name)
			brand, _ = Brand.objects.get_or_create(
				name=directory.name,
				defaults=data
			)
			self.download_assets(brand, assets)
			self.make_notes(brand, notes)
			with os.scandir(directory) as it:
				for entry in it:
					if entry.is_dir() and len(entry.name) == 4:
						try:
							_ = int(entry.name)
							self._scan_model_year(brand, entry, )
						except ValueError:
							pass
		finally:
			self._directory.pop()
		return brand

	def _scan_model_year(self, brand, directory):
		self._directory.append(directory)
		try:
			with os.scandir(directory) as it:
				for entry in it:
					if entry.name.endswith(".json"):
						self.make_frame(brand, entry)
		finally:
			self._directory.pop()
		return brand

	def make_frame(self, brand, entry):
		with codecs.open(entry, 'r', 'utf-8') as fh:
			data = json.load(fh)

		frame_name = data["name"]
		frame_label = f"Brand '{brand.name}', frame '{frame_name}"
		logger.info("Importing Frame %s %s %s", brand, frame_name, data) #data["yearFrom"])
		bike_type: str = data.get("bikeType")
		if bike_type:
			data["bikeType"] = self.get_reference(frame_label, BikeType, bike_type)
		material: str = data.get("material")
		if material:
			data["material"] = self.get_reference(frame_label, Material, material)
		assets = data.pop("assets", None)
		notes = data.pop("notes", None)
		sizes = data.pop("sizes", None)

		frame, _ = Frame.objects.get_or_create(
			brand=brand,
			name=frame_name,
			yearFrom=int(self._directory[-1].name),
			defaults=data
		)
		for size in sizes:
			frame_size = size["name"]
			logger.info("Importing Frame %s %s %s Size '%s'", brand.name, frame.name, frame.yearFrom, frame_size)
			size, _ = FrameSize.objects.get_or_create(
				frame=frame,
				name=frame_size,
				defaults=size
			)
		self.download_assets(frame, assets)
		self.make_notes(frame, notes)
		return frame

	def make_notes(self, entity, notes):
		if not notes:
			return
		for note in notes:
			entity.add_note(note, self.user)

	def download_assets(self, entity, assets):
		if not assets:
			return
		for asset in assets:
			logger.info("Downloading asset %s for %s", str(asset), entity.name)
			tag = asset["tag"]
			name = asset["name"]
			content = asset["data"]

			if content.startswith("http"):
				with urllib.request.urlopen(content) as resp:
					asset_data = resp.read()
			else:
				with open(os.path.join(self._directory[-1], content), 'rb') as fh:
					asset_data = fh.read()
			entity.upsert_asset(name, tag, asset_data)

	def import_bike_data(self, directory):
		try:
			brand = self.make_brand(directory)
		except Exception as e:
			logger.exception("Exception importing", exc_info=e)
			self.log_error("Exception importing: %s", e)
