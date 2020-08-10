import io
import itertools
import logging
import threading
import urllib.request

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import slowfit.util

from ..models.base import Country
from ..models.base import BikeType
from ..models.base import Material
from ..models.bikes import Brand
from ..models.bikes import Frame
from ..models.bikes import FrameSize
from ..models.imports import ImportLog, START, BUSY, ERRORS, OK


class Credentials(dict):
	def __init__(self, old, oauth2_credentials):
		super(Credentials, self).__init__()
		if old:
			logging.debug("old: token: %s, refresh_token: %s", old["token"], old["refresh_token"])
		else:
			logging.debug("old is None")
		logging.debug("oauth2: token: %s, refresh_token: %s",
			oauth2_credentials.token, oauth2_credentials.refresh_token)
		self._initializing = True
		self["token"] = old["token"] if old else None
		self["refresh_token"] = old["refresh_token"] if old else None
		self["token_uri"] = old["token_uri"] if old else None
		self["client_id"] = old["client_id"] if old else None
		self["client_secret"] = old["client_secret"] if old else None
		self["scopes"] = old["scopes"] if old else None
	
		if oauth2_credentials.token:
			self["token"] = oauth2_credentials.token
		if oauth2_credentials.refresh_token:
			self["refresh_token"] = oauth2_credentials.token
		if oauth2_credentials.token_uri:
			self["token_uri"] = oauth2_credentials.token
		if oauth2_credentials.client_id:
			self["client_id"] = oauth2_credentials.token
		if oauth2_credentials.client_secret:
			self["client_secret"] = oauth2_credentials.token
		if oauth2_credentials.scopes:
			self["scopes"] = oauth2_credentials.token
		self._initializing = False
		logging.debug("self: token: %s, refresh_token: %s", self["token"], self["refresh_token"])

	def __setitem__(self, key, value):
		if self._initializing:
			super(Credentials, self).__setitem__(key, value)


ColBrandName = 0
ColCountry = 1
ColBrandWebsite = 2
ColFrameName = 3
ColFrameWebPage = 4
ColMaterial = 5
ColBikeType = 6
ColYearFrom = 7
ColYearTo = 8
ColSize = 9
ColStack = 10
ColReach = 11
ColHTAngle = 12
ColBrandAssetTag = 13
ColBrandAsset = 14
ColFrameAssetTag = 15
ColFrameAsset = 16

SCOPES = [
	'https://www.googleapis.com/auth/drive.readonly',
	'https://www.googleapis.com/auth/drive.metadata.readonly',
	'https://www.googleapis.com/auth/spreadsheets.readonly',
]

logger = logging.getLogger(__name__)


class GImportSession(threading.Thread):
	def __init__(self, credentials, user, sheet_id=""):
		super(GImportSession, self).__init__()
		self.credentials = credentials
		self.token = None
		self.current = None
		self.row = None
		self.assets = {}
		self.sheetId = sheet_id
		self.slowfitId = ""
		self.driveSrv = None
		self.sheetSrv = None
		self.user = user
		self.log = None

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
			raise GImportSession.ReferenceObjectDoesNotExist(entity, model, key, foreign_field)
		elif len(objects) > 1:
			raise GImportSession.ReferenceObjectNotUnique(entity, model, key, foreign_field)
		else:
			return objects[0]

	def import_sheet(self, sheet_id=None):
		try:
			self.sheetId = sheet_id or "1Udfg-EYl2q0JPPvfhUrA6_3HPDOFXX8wBscjtPjBOR8"
			self.log = ImportLog()
			self.log.importedBy = self.user
			self.log.sheetID = self.sheetId
			self.set_status(START)
			self.start()
		except Exception as e:
			pass

	def run(self):
		try:
			self.sheetSrv = build('sheets', 'v4', credentials=self.credentials, cache_discovery=False)

			# getCall := gis.sheetSrv.Spreadsheets.Get(gis.sheetId)
			# getCall.IncludeGridData(true)
			# ss, err := getCall.Do()
			# if err != nil; {
			# 	gis.LogError("Error getting slowfit sheet %s: %v", gis.sheetId, err)
			# 	return
			# }
			ss = self.sheetSrv.spreadsheets().get(spreadsheetId=self.sheetId, includeGridData=True).execute()
			self.log.title = ss["properties"]["title"]
			self.set_status(BUSY)

			for s in ss.get("sheets", []):
				n = s["properties"]["title"]
				if n == "Data":
					self.current = s["data"][0]
					self.import_data()

			for s in ss["sheets"]:
				n = s["properties"]["title"]
				if n != "Data":
					self.current = s["data"][0]
					self.import_bike_data()

			if self.log.status != ERRORS:
				self.set_status(OK)
		except Exception as e:
			logger.exception("Exception caught: ", exc_info=e)
			self.log_error(str(e))

	def import_data(self):
		fields = []
		model_name = None
		for self.row in self.current["rowData"]:
			ev = self.row["values"][0].get("effectiveValue")
			if ev is not None:
				model_name = ev["stringValue"]
				fields = [v["effectiveValue"]["stringValue"] for v in self.row["values"][1:]]
			elif model_name is not None:
				self.import_model(model_name, fields)

	def import_model(self, model_name, fields):
		model = slowfit.util.resolve("slowfit.models." + model_name)
		args = {"defaults": {}}
		defaults = args["defaults"]
		key = None
		for fld, v in itertools.zip_longest(fields, self.row["values"][1:]):
			ev = v["effectiveValue"]
			if key is None:
				key = ev["stringValue"]
				args[fld] = key
			else:
				defaults[fld] = ev.get("numberValue",  ev.get("stringValue", ""))
		try:
			model.objects.get_or_create(**args)
		except Exception as e:
			self.log_error("Exception importing '{0}' '{1}': {2}", model_name, key, e)

	def make_brand(self):
		brand_name = self.row["values"][ColBrandName]["effectiveValue"]["stringValue"]
		logger.info("Importing Brand '%s'", brand_name)
		brand = None
		url = self.row["values"][ColBrandWebsite]["effectiveValue"]["stringValue"] \
			if self.row["values"][ColBrandWebsite]["effectiveValue"] \
			else None
		country_code: str = self.row["values"][ColCountry]["effectiveValue"]["stringValue"]
		country = self.get_reference(brand_name, Country, country_code.lower(), "isoCode")
		brand, _ = Brand.objects.get_or_create(
			name=brand_name,
			defaults={
				"URL": url,
				"country": country,
			}
		)
		return brand

	def make_frame(self, brand):
		frame_name = self.row["values"][ColFrameName]["effectiveValue"]["stringValue"]
		y = self.row["values"][ColYearFrom]["userEnteredValue"]["numberValue"]
		logger.info("Importing Frame %s %s %s", brand, frame_name, y)
		frame = None

		url = self.row["values"][ColFrameWebPage]["effectiveValue"]["stringValue"] \
			if self.row["values"][ColFrameWebPage]["effectiveValue"]\
			else None
		year_to = self.row["values"][ColYearTo]["effectiveValue"]["numberValue"] \
			if self.row["values"][ColYearTo]["effectiveValue"]\
			else None
		bike_type_name = self.row["values"][ColBikeType]["effectiveValue"]["stringValue"]
		bike_type = self.get_reference(f"Brand '{brand.name}', frame '{frame_name}", BikeType, bike_type_name)
		material_name = self.row["values"][ColMaterial]["effectiveValue"]["stringValue"]
		material = self.get_reference(f"Brand '{brand.name}', frame '{frame_name}", Material, material_name)
		if material is None:
			self.log_error(f"Brand '{brand.name}', frame '{frame_name}': Unknown material '{material_name}'")
			return
		frame, _ = Frame.objects.get_or_create(
			brand=brand,
			name=frame_name,
			defaults={
				"yearFrom": y,
				"yearTo": year_to,
				"imported": self.log,
				"URL": url,
				"bikeType": bike_type,
				"material": material
			})
		return frame

	def make_frame_size(self, brand, frame):
		frame_size = self.row["values"][ColSize]["userEnteredValue"]["stringValue"]
		logger.info("Importing Frame %s %s %s Size '%s'", brand.name, frame.name, frame.yearFrom, frame_size)
		stack = self.row["values"][ColStack]["userEnteredValue"]["numberValue"]
		reach = self.row["values"][ColReach]["userEnteredValue"]["numberValue"]
		ht_angle = self.row["values"][ColHTAngle]["userEnteredValue"]["numberValue"]
		size, _ = FrameSize.objects.get_or_create(
			frame=frame,
			name=frame_size,
			defaults={
				"stack": stack,
				"reach": reach,
				"headTubeAngle": ht_angle
			})
		size.save()
		return size

	def download_assets(self, entity, ix):
		if entity is None or \
				len(self.row["values"]) <= ix or \
				self.row["values"][ix] is None or \
				"effectiveValue" not in self.row["values"][ix]:
			return

		tag = self.row["values"][ix]["effectiveValue"]["stringValue"]
		logger.info("Download assets for %s tag %s", entity.name, tag)
		asset = self.row["values"][ix+1]["effectiveValue"]["stringValue"]
		if tag == "notes":
			entity.add_note(asset, self.user)
			return

		asset_data = None
		if asset.startswith("http"):
			with urllib.request.urlopen(asset) as resp:
				asset_data = resp.read()
		else:
			asset_id = self.assets.get(asset)
			if id is not None:
				req = self.driveSrv.files().get_media(fileId=asset_id)
				buffer = io.BytesIO()
				downloader = MediaIoBaseDownload(buffer, req)
				done = False
				while done is False:
					# _, done = downloader.next_chunk()
					try:
						status, done = downloader.next_chunk()
					except:
						buffer.close()
						raise
				buffer.seek(0)
				asset_data = buffer.read()
			else:
				self.log_error("Unknown asset '{0}'", asset)
				return
		entity.upsert_asset(asset, tag, asset_data)

	def import_bike_data(self):
		brand = None
		frame = None
		try:
			for self.row in self.current["rowData"][1:]:
				if self.row["values"][ColBrandName] and "effectiveValue" in self.row["values"][ColBrandName] is not None:
					brand = self.make_brand()
					if brand is not None:
						self.get_assets(brand.name)
				if brand is not None:
					if self.row["values"][ColFrameName] and "effectiveValue" in self.row["values"][ColFrameName] is not None:
						frame = self.make_frame(brand)
					self.download_assets(brand, ColBrandAssetTag)
				if frame is not None:
					if self.row["values"][ColSize] and "effectiveValue" in self.row["values"][ColSize]:
						self.make_frame_size(brand, frame)
					self.download_assets(frame, ColFrameAssetTag)
		except Exception as e:
			logger.exception("Exception importing", exc_info=e)
			self.log_error("Exception importing: %s", e)

	def get_assets(self, brand):
		self.assets = {}
		if self.driveSrv is None:
			self.driveSrv = build('drive', 'v3', credentials=self.credentials, cache_discovery=False)

		if self.slowfitId == "":
			results = self.driveSrv.files().list(q="name = 'slowfit'", spaces="drive", fields="files(id, name)").execute()
			items = results.get('files', [])
			if items and len(items) > 0:
				slowfit = items[0]
				logger.info("Slowfit Folder Id %s", slowfit["id"])
				self.slowfitId = slowfit["id"]
		assert self.slowfitId != ""

		results = self.driveSrv.files().list(
			q=f"name = '{brand}' and '{self.slowfitId}' in parents and mimeType = 'application/vnd.google-apps.folder'",
			spaces="drive",
			fields="files(id, name)").execute()
		items = results.get('files', [])
		brand_id = ""
		if items and len(items) > 0:
			brand_file = items[0]
			logger.info("Brand %s Folder Id %s\n", brand, brand_file["id"])
			brand_id = brand_file["id"]
		if brand_id == "":
			return

		results = self.driveSrv.files().list(
			q=f"'{brand_id}' in parents",
			spaces="drive",
			fields="files(id, name)").execute()
		for ff in results.get('files', []):
			self.assets[ff["name"]] = ff["id"]

		logger.info("assets: %s", self.assets)
