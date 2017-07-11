from django.utils.dateparse import parse_datetime

from gservices.services.base import BaseService
from django.conf import settings


class BaseCalendar(BaseService):
    _SERVICE = settings.CALENDAR_SERVICE
    _create_method = 'insert'

    @property
    def title(self):
        return self._get_property('summary')


class Calendar(BaseCalendar):
    _RESOURCE = 'calendars'

    @property
    def calendar_id(self):
        return self._get_property('id')

    def _create_payload(self, title, *args, **kwargs):
        return {'body': {'summary': title}}

    def _update_payload(self, title, *args, **kwargs):
        return {'calendarId': self.calendar_id,
                'body': {'summary': title}}

    def _delete_payload(self, *args, **kwargs):
        return {'calendarId': self.calendar_id}

    def _list_events_payload(self, page_token=None):
        d = {'calendarId': self.calendar_id}
        if page_token:
            d['pageToken'] = page_token

        return d

    def list_events(self, *args, **kwargs):
        return self._send_request('list', self._list_events_payload(*args, **kwargs), 'events')


class Event(BaseCalendar):
    _RESOURCE = 'events'
    _update_method = 'patch'

    @property
    def event_id(self):
        return self._get_property('id')

    @property
    def start_time(self):
        return parse_datetime(self._get_property('start')['dateTime'])

    @property
    def end_time(self):
        return parse_datetime(self._get_property('end')['dateTime'])

    def _create_payload(self, calendar_id, start_time, end_time, title=None, *args, **kwargs):
        b = {'start': start_time,
             'end': end_time}

        if title:
            b['summary'] = title

        d = {'calendarId': calendar_id,
             'body': b}

        return d

    def _update_payload(self, calendar_id, start_time=None, end_time=None, title=None, *args, **kwargs):
        b = {}

        if start_time:
            b['start'] = start_time

        if end_time:
            b['end'] = end_time

        if title:
            b['summary'] = title

        d = {'calendarId': calendar_id,
             'eventId': self.event_id,
             'body': b}

        return d

    def _delete_payload(self, calendar_id, *args, **kwargs):

        return {'calendarId': calendar_id,
                'eventId': self.event_id}
