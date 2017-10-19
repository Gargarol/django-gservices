# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from time import sleep

from django import forms
from django.test import TestCase
from django.urls import reverse
from pytz import timezone
from gservices.models import TestFileUploadModel

from gservices.services import drive, calendar, admin
import unittest


class File(TestCase):

    def test_upload_file(self):
        url = reverse('test-file-form')
        with open('test.txt') as f:
            response = self.client.post(url, data={'test_file': f})
            files = TestFileUploadModel.objects.all()
            for file in files:
                file.test_file.delete()
            self.assertEqual(len(files), 1)


class TeamDrive(unittest.TestCase):

    def test_create_team_drive(self):
        name = 'Test Drive'
        team_drive = drive.TeamDrive()
        team_drive.create(name=name)
        self.assertEqual(team_drive.name, name)
        team_drive.delete()

    def test_update_team_drive(self):
        name = 'Test Drive For Update'
        update_name = 'Updated Drive'
        team_drive = drive.TeamDrive()
        team_drive.create(name=name)
        self.assertEqual(team_drive.name, name)
        team_drive.update(name=update_name)
        self.assertEqual(team_drive.name, update_name)
        team_drive.delete()

    def test_delete_team_drive(self):
        name = 'Test Drive For Delete'
        team_drive = drive.TeamDrive()
        team_drive.create(name=name)
        team_drive.delete()
        self.assertRaises(TypeError, team_drive.drive_id)
        self.assertRaises(TypeError, team_drive.name)


class Folder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.team_drive = drive.TeamDrive()
        cls.team_drive.create(name='Folder Test Drive')

    def test_create_folder(self):
        name = 'Test Folder'
        parents = [self.team_drive.drive_id]
        folder = drive.Folder()
        folder.create(name=name, parents=parents)
        self.assertEqual(folder.name, name)
        self.assertEqual(folder.parents, parents)
        folder.delete()

    def test_update_folder(self):
        name = 'Test Folder To Update'
        update_name = 'Updated Folder Name'
        parents = [self.team_drive.drive_id]
        folder = drive.Folder()
        folder.create(name=name, parents=parents)
        folder.update(name=update_name)
        self.assertEqual(folder.name, update_name)
        folder.delete()

    def test_list_folders(self):
        name = 'Test Folder'
        child_folder_name = 'Child Folder'
        parents = [self.team_drive.drive_id]
        parent_folder = drive.Folder()
        parent_folder.create(name=name, parents=parents)
        child_parents = [parent_folder.drive_id]
        child_folder = drive.Folder()
        child_folder.create(name=child_folder_name, parents=child_parents)
        r = parent_folder.list()
        self.assertEqual(len(r['files']), 1)
        self.assertEqual(r['files'][0]['name'], child_folder_name)
        child_folder.delete()
        parent_folder.delete()

    @classmethod
    def tearDownClass(cls):
        cls.team_drive.delete()


class Calendar(unittest.TestCase):

    def test_create_calendar(self):
        name = 'Test Calendar'
        c = calendar.Calendar()
        c.create(title=name)
        self.assertEqual(c.title, name)
        c.delete()

    def test_update_calendar(self):
        name = 'Test Calendar For Update'
        update_name = 'Updated Calendar'
        c = calendar.Calendar()
        c.create(title=name)
        self.assertEqual(c.title, name)
        c.update(title=update_name)
        self.assertEqual(c.title, update_name)
        c.delete()

    def test_delete_calendar(self):
        name = 'Test Calendar For Delete'
        c = calendar.Calendar()
        c.create(title=name)
        c.delete()
        self.assertRaises(TypeError, c.calendar_id)
        self.assertRaises(TypeError, c.title)


class Events(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.calendar = calendar.Calendar()
        cls.calendar.create(title='Test Calendar For Events')

    def test_create_event(self):
        event = calendar.Event()
        start_time = datetime.datetime.now()
        time_zone = 'America/Phoenix'
        end_time = datetime.datetime.now() + datetime.timedelta(days=1)
        event.create(calendar_id=self.calendar.calendar_id,
                     start_time={'dateTime': start_time.isoformat(), 'timeZone': time_zone},
                     end_time={'dateTime': end_time.isoformat(), 'timeZone': time_zone})
        self.assertEqual(len(self.calendar.list_events()['items']), 1)
        event.delete(calendar_id=self.calendar.calendar_id)

    def test_update_event(self):
        event = calendar.Event()
        start_time = datetime.datetime.now()
        time_zone = 'America/Phoenix'
        end_time = datetime.datetime.now() + datetime.timedelta(days=1)
        updated_end_time = datetime.datetime.now() + datetime.timedelta(days=2)
        event.create(calendar_id=self.calendar.calendar_id,
                     start_time={'dateTime': start_time.isoformat(), 'timeZone': time_zone},
                     end_time={'dateTime': end_time.isoformat(), 'timeZone': time_zone})
        event.update(calendar_id=self.calendar.calendar_id,
                     end_time={'dateTime': updated_end_time.isoformat(), 'timeZone': time_zone})
        self.assertEqual(event.end_time.strftime('%D'), updated_end_time.astimezone(timezone(time_zone)).strftime('%D'))
        event.delete(calendar_id=self.calendar.calendar_id)

    def test_delete_event(self):
        event = calendar.Event()
        start_time = datetime.datetime.now()
        time_zone = 'America/Phoenix'
        end_time = datetime.datetime.now() + datetime.timedelta(days=1)
        event.create(calendar_id=self.calendar.calendar_id,
                     start_time={'dateTime': start_time.isoformat(), 'timeZone': time_zone},
                     end_time={'dateTime': end_time.isoformat(), 'timeZone': time_zone})
        event.delete(calendar_id=self.calendar.calendar_id)
        self.assertEqual(len(self.calendar.list_events()['items']), 0)

    @classmethod
    def tearDownClass(cls):
        cls.calendar.delete()


class Group(unittest.TestCase):
    """
    The need for sleep needs to be looked at more closely. It seems to be a delay between receiving the response
    and when google is actually adding the items to the service. Should have no real world consequences.
    """
    @classmethod
    def setUpClass(cls):
        cls.member_test_group = admin.Group()
        cls.member_test_group.create(local_part='member_test_group')
        sleep(1)

    def test_create_group(self):
        group = admin.Group()
        group.create(local_part='test_group')
        self.assertEqual(group.email, 'test_group@iandowell.com')
        sleep(1)
        group.delete()

    def test_update_group(self):
        updated_name = 'Test Group Updated'
        group = admin.Group()
        group.create(local_part='test_group_update')
        self.assertEqual(group.email, 'test_group_update@iandowell.com')
        sleep(1)
        group.update(name=updated_name)
        self.assertEqual(group.name, updated_name)
        sleep(1)
        group.delete()

    def test_group_member(self):
        self.member_test_group.add_member('ian@iandowell.com')
        member_list = self.member_test_group.list_members()
        self.assertEqual(len(member_list['members']), 1)
        self.member_test_group.delete_member('ian@iandowell.com')
        member_list = self.member_test_group.list_members()
        self.assertRaises(KeyError, lambda: member_list['members'])


    @classmethod
    def tearDownClass(cls):
        cls.member_test_group.delete()
