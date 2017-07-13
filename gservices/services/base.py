import json

import httplib2
from django.conf import settings


class ResourceCreateException(Exception):
    pass


class ResourceDeleteException(Exception):
    pass


class ResourceUpdateException(Exception):
    pass


class BaseService(object):
    _SERVICE = None
    _RESOURCE = None
    _create_method = 'create'
    _update_method = 'update'
    _delete_method = 'delete'
    _create_exception_message = None
    _update_exception_message = None
    _delete_exception_message = None
    _data = None

    def __init__(self, credentials=None, data=None, *args, **kwargs):
        if credentials:
            self.credentials = credentials
        else:
            self.credentials = settings.DELEGATED_CREDENTIALS

        if data:
            self._data = self._parse_data(data)

    def _parse_data(self, data):
        if type(data) is dict:
            return data
        elif type(data) is basestring:
            return json.loads(data)
        elif type(data) is str:
            return json.loads(data)

    @property
    def request_http(self):
        r_http = httplib2.Http()
        r_http = self.credentials.authorize(r_http)
        return r_http

    def _get_property(self, key):
        try:
            return self._data[key]
        except AttributeError as e:
            print e
        except KeyError as e:
            print e
        except TypeError as e:
            print e

    def _create_payload(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        if self._data is not None:
            raise ResourceCreateException(self._create_exception_message)

        self._data = self._send_request(self._create_method, self._create_payload(*args, **kwargs))

    def _update_payload(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        if self._data is None:
            raise ResourceUpdateException(self._update_exception_message)

        self._data = self._send_request(self._update_method, self._update_payload(*args, **kwargs))

    def _delete_payload(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        if self._data is None:
            raise ResourceDeleteException(self._delete_exception_message)

        self._data = self._send_request(self._delete_method, self._delete_payload(*args, **kwargs))

    def _send_request(self, method, payload, resource=None):
        if not resource:
            resource = self._RESOURCE

        # The basic pattern for a google service request
        # SERVICE.RESOURCE().METHOD(PAYLOAD).execute(AUTHORIZED HTTP OBJECT)
        try:
            return getattr(getattr(self._SERVICE, resource)(), method)(**payload).execute(self.request_http)
        except TypeError as e:
            print e.message

    def json(self):
        return json.dumps(self._data)
