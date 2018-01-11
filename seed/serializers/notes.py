# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2017, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
from rest_framework import serializers
from seed.models import Note
from seed.serializers.base import ChoiceField


class NoteSerializer(serializers.ModelSerializer):
    note_type = ChoiceField(choices=Note.NOTE_TYPES)

    class Meta:
        model = Note
        fields = '__all__'
