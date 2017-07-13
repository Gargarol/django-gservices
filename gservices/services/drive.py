import uuid

from gservices.services.base import BaseService
from django.conf import settings


class BaseDrive(BaseService):
    _SERVICE = settings.DRIVE_SERVICE

    @property
    def drive_id(self):
        return self._get_property('id')

    @property
    def name(self):
        return self._get_property('name')


class ListMixin(object):
    _list_method = 'list'

    def _list_payload(self, *args, **kwargs):
        raise NotImplementedError

    def list(self, *args, **kwargs):
        return self._send_request(self._list_method, self._list_payload(*args, **kwargs))


class TeamDrive(BaseDrive):
    _RESOURCE = 'teamdrives'
    _create_exception_message = 'Data already set for this team drive.'
    _update_exception_message = 'You must first create a team drive.'
    _delete_exception_message = 'You must first create a team drive.'

    @property
    def url(self):
        return 'https://drive.google.com/drive/u/1/folders/{0}'.format(self._data['id'])

    def _create_payload(self, name):
        return {'requestId': uuid.uuid4(),
                'body': {'name': name}}

    def _update_payload(self, name):
        return {'teamDriveId': self.drive_id,
                'body': {'name': name}}

    def _delete_payload(self, **kwargs):
        return {'teamDriveId': self.drive_id}


class BaseFile(BaseDrive):
    _RESOURCE = 'files'

    @property
    def _drive_fields(self):
        return ['kind',
                'id',
                'name',
                'mimeType',
                'description',
                'parents',
                'webViewLink',
                'webContentLink',
                'iconLink',
                'createdTime',
                'teamDriveId',
                'hasThumbnail',
                'thumbnailLink']

    @property
    def parents(self):
        return self._get_property('parents')

    @property
    def team_drive_id(self):
        return self._get_property('teamDriveId')


class Folder(ListMixin, BaseFile):
    _GOOGLE_DRIVE_FOLDER_MIMETYPE = "application/vnd.google-apps.folder"
    _create_exception_message = 'Data already set for this folder.'
    _update_exception_message = 'You must first create a folder.'
    _delete_exception_message = 'You must first create a folder.'

    def _create_payload(self, name, parents, **kwargs):
        meta_data = {'name': name,
                     'mimeType': self._GOOGLE_DRIVE_FOLDER_MIMETYPE,
                     'parents': parents}

        return {'body': meta_data,
                'supportsTeamDrives': True,
                'fields': ','.join(self._drive_fields)}

    def _update_payload(self, name=None, add_parents=None, remove_parents=None, **kwargs):

        d = {'body': {'name': name if name else self.name},
             'supportsTeamDrives': True,
             'fields': ','.join(self._drive_fields),
             'fileId': self.drive_id}

        if add_parents:
            d['addParents'] = ','.join(add_parents)

        if remove_parents:
            d['removeParents'] = ','.join(remove_parents)

        return d

    def _delete_payload(self, **kwargs):
        return {'supportsTeamDrives': True,
                'fileId': self.drive_id}

    def _list_payload(self, corpora='teamDrive', page_token=None, *args, **kwargs):
        _q = "'{0}' in parents".format(self.drive_id)
        d = {'q': _q,
             'corpora': corpora,
             'fields': 'nextPageToken, files({0})'.format(','.join(self._drive_fields)),
             'pageToken': page_token}

        if self.team_drive_id:

            d['teamDriveId'] = self.team_drive_id
            d['supportsTeamDrives'] = True
            d['includeTeamDriveItems'] = True

        return d