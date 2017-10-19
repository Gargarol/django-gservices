import json

from django.contrib.postgres.fields import JSONField
from django.db.models import FileField
from django import forms

# from django.forms import FileField
from django.forms import FileInput

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

        return self.service_object(data=value)

    def get_prep_value(self, value):
        if value is None:
            return value
        else:
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


class GoogleDriveFileWidget(FileInput):
    pass


class GoogleDriveFileField(BaseGoogleServiceField):
    service_object = drive.File

    def __init__(self, *args, **kwargs):
        get_parents_func = kwargs.pop('get_parents_func', None)

        self.get_parents_func = get_parents_func
        super(GoogleDriveFileField, self).__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        value = value._data
        super(GoogleDriveFileField, self).validate(value, model_instance)

    def save_form_data(self, instance, data):
        field = getattr(instance, self.name)
        if data is not None:
            if field:
                pass
            else:
                try:
                    parents = self.get_parents_func(instance)
                    service = self.service_object()
                    service.create(parents=parents, in_memory_file=data)
                    setattr(instance, self.name, service)
                    print instance
                except TypeError as e:
                    pass

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.FileField}
        # If a file has been provided previously, then the form doesn't require
        # that a new file is provided this time.
        # The code to mark the form field as not required is used by
        # form_for_instance, but can probably be removed once form_for_instance
        # is gone. ModelForm uses a different method to check for an existing file.
        if 'initial' in kwargs:
            defaults['required'] = False
        defaults.update(kwargs)
        return super(GoogleDriveFileField, self).formfield(**defaults)
