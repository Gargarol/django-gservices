import json

from django.contrib.postgres.fields import JSONField
from gservices.services import admin, calendar, drive


class BaseGoogleServiceField(JSONField):
    service_object = None

    def from_db_value(self, value, expression, connection, context):

        if value is None:
            return None

        return self.service_object(data=value)

    def to_python(self, value):

        if isinstance(value, self.service_object):
            return value

        if value is None:
            return value

        v = json.loads(value)
        return self.service_object(data=value)

    def get_prep_value(self, value):
        return value.json()


class GoogleGroupField(BaseGoogleServiceField):
    service_object = admin.Group


class GoogleTeamDriveField(BaseGoogleServiceField):
    service_object = drive.TeamDrive


class GoogleDriveFolderField(BaseGoogleServiceField):
    service_object = drive.Folder


class GoogleCalendarField(BaseGoogleServiceField):
    service_object = calendar.Calendar


class GoogleCalendarEventField(BaseGoogleServiceField):
    service_object = calendar.Event
