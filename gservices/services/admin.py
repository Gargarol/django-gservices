from gservices.services.base import BaseService
from django.conf import settings


class BaseAdmin(BaseService):
    _SERVICE = settings.ADMIN_SERVICE
    _create_method = 'insert'
    _update_method = 'update'


class Group(BaseAdmin):
    _RESOURCE = 'groups'
    _MEMBER_RESOURCE = 'members'
    _list_method = 'list'

    @property
    def email(self):
        return self._get_property('email')

    @property
    def name(self):
        return self._get_property('name')

    def _get_email(self, local_part):
        return '{0}@{1}'.format(local_part, settings.DOMAIN)

    def _create_payload(self, local_part, name=None, description=None, *args, **kwargs):
        d = {'body': {'email': self._get_email(local_part)}}

        if name:
            d['name'] = name

        if description:
            d['description'] = description

        return d

    def _update_payload(self, name=None, description=None, *args, **kwargs):
        d = {'groupKey': self.email}
        body = {}

        if name:
            body['name'] = name

        if description:
            body['description'] = description

        if any(body):
            d['body'] = body

        return d

    def _delete_payload(self, *args, **kwargs):
        return {'groupKey': self.email}

    def _add_member_payload(self, email, *args, **kwargs):
        return {'groupKey': self.email, 'body': {'email': email}}

    def add_member(self, *args, **kwargs):
        self._send_request(self._create_method, self._add_member_payload(*args, **kwargs), resource=self._MEMBER_RESOURCE)

    def _list_member_payload(self, *args, **kwargs):
        return {'groupKey': self.email}

    def list_members(self, *args, **kwargs):
        return self._send_request(self._list_method, self._list_member_payload(*args, **kwargs), resource=self._MEMBER_RESOURCE)

    def _delete_member_payload(self, member_key, *args, **kwargs):
        return {'groupKey': self.email, 'memberKey': member_key}

    def delete_member(self, *args, **kwargs):
        self._send_request(self._delete_method, self._delete_member_payload(*args, **kwargs), resource=self._MEMBER_RESOURCE)