from django.contrib.auth.models import User
from django.db import models

START = "Start"
BUSY = "Busy"
OK = "Done"
ERRORS = "Errors"
STATUS_CHOICES = [
	(START, START),
	(BUSY, BUSY),
	(OK, OK),
	(ERRORS, ERRORS),
]


class ImportLog(models.Model):
	class Meta:
		ordering = ("-timestamp", )

	timestamp = models.DateTimeField(auto_now_add=True)
	importedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	reference = models.TextField(null=True)
	title = models.TextField(null=True)
	status = models.TextField(choices=STATUS_CHOICES)
	frameCount = models.PositiveSmallIntegerField(default=0)
	log = models.TextField(null=True)

	def log_error(self, fmt, *args):
		msg = fmt.format(*args)
		if msg != "":
			self.log = "{0}{0}\n".format(self.log, msg)
		self.set_status(ERRORS)

	def set_status(self, status):
		self.status = status
		self.save()
