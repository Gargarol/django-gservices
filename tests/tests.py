import json

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from gservices.tests import TeamDrive, Events, Calendar, Folder, Group, File
# from gservices.tests import File