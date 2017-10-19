# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .fields import GoogleDriveFileField
from django.db import models


def get_parents_func(instance):

    return ['0ANe6vNTUyaHqUk9PVA']


class TestFileUploadModel(models.Model):
    test_file = GoogleDriveFileField(get_parents_func=get_parents_func)
