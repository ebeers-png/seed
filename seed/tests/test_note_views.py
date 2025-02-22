# !/usr/bin/env python
# encoding: utf-8
"""
SEED Platform (TM), Copyright (c) Alliance for Sustainable Energy, LLC, and other contributors.
See also https://github.com/seed-platform/seed/main/LICENSE.md

:author nicholas.long@nrel.gov
"""
import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from seed.landing.models import SEEDUser as User
from seed.models import NoteEvent
from seed.test_helpers.fake import (
    FakeNoteFactory,
    FakePropertyViewFactory,
    FakeTaxLotViewFactory
)
from seed.utils.organizations import create_organization


class NoteViewTests(TestCase):
    def setUp(self):
        user_details = {
            'username': 'test_user@demo.com',
            'password': 'test_pass',
            'email': 'test_user@demo.com'
        }
        self.user = User.objects.create_superuser(**user_details)
        self.org, _, _ = create_organization(self.user)

        # Fake Factories
        self.property_view_factory = FakePropertyViewFactory(organization=self.org)
        self.taxlot_view_factory = FakeTaxLotViewFactory(organization=self.org)
        self.note_factory = FakeNoteFactory(organization=self.org, user=self.user)

        self.client.login(**user_details)

        # create a property view with some notes
        self.pv = self.property_view_factory.get_property_view(organization=self.org)
        self.note1 = self.note_factory.get_note()
        self.note2 = self.note_factory.get_log_note()

        self.pv.notes.add(self.note1)
        self.pv.notes.add(self.note2)

        # create a taxlot with some views
        self.tl = self.taxlot_view_factory.get_taxlot_view(organization=self.org)
        self.note3 = self.note_factory.get_note()
        self.note4 = self.note_factory.get_log_note()
        self.tl.notes.add(self.note3)
        self.tl.notes.add(self.note4)

    def test_get_notes_property(self):
        url = reverse('api:v3:property-notes-list', args=[self.pv.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = json.loads(response.content)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['note_type'], 'Log')
        self.assertEqual(results[0]['user_id'], self.user.pk)

        # most recent log is displayed first
        expected_log_data = {
            'property_state': [
                {
                    'field': 'address_line_1',
                    'previous_value': '123 Main Street',
                    'new_value': '742 Evergreen Terrace'
                }
            ]
        }
        self.assertEqual(results[0]['log_data'], expected_log_data)
        self.assertEqual(results[1]['note_type'], 'Note')

    def test_create_note_property(self):
        url = reverse('api:v3:property-notes-list', args=[self.pv.pk])

        payload = {
            "note_type": "Note",
            "name": "A New Note",
            "text": "This building is much bigger than reported",
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        result = json.loads(response.content)

        # check that the note was attached to the property
        self.assertEqual(result['note_type'], 'Note')
        self.assertEqual(result['text'], payload['text'])
        self.assertEqual(result['property_view_id'], self.pv.pk)
        self.assertTrue('taxlot_view_id' not in result)
        self.assertEqual(result['organization_id'], self.org.pk)
        self.assertEqual(result['user_id'], self.user.pk)

        events = NoteEvent.objects.all().values()
        self.assertEqual(1, len(events))
        event = events[0]
        self.assertEqual(result["id"], event["note_id"])

    def test_create_note_taxlot(self):
        url = reverse('api:v3:taxlot-notes-list', args=[self.tl.pk])

        payload = {
            "note_type": "Note",
            "name": "A New Note",
            "text": "The taxlot is not correct",
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        result = json.loads(response.content)

        # check that the note was attached to the property
        self.assertEqual(result['note_type'], 'Note')
        self.assertEqual(result['text'], payload['text'])
        self.assertTrue('property_view_id' not in result)
        self.assertEqual(result['taxlot_view_id'], self.tl.pk)

    def test_update_note(self):
        url = reverse('api:v3:taxlot-notes-detail', args=[self.tl.pk, self.note3.pk])

        payload = {
            "name": "update, validation should fail"
        }
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content),
                         {"text": ["This field is required."], "note_type": ["This field is required."]})

        payload = {
            "name": "update",
            "text": "new data with put",
            "note_type": "Note"
        }
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        result = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result['name'], payload['name'])
        self.assertEqual(result['text'], payload['text'])

    def test_get_detail_and_delete_note(self):
        note5 = self.note_factory.get_note()
        self.pv.notes.add(note5)

        url = reverse('api:v3:property-notes-detail', args=[self.pv.pk, note5.pk])
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content)
        self.assertEqual(result['property_view_id'], self.pv.pk)
        self.assertEqual(result['id'], note5.pk)

        # now delete the note
        response = self.client.delete(url, content_type='application/json')
        # delete returns no content
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # note should return nothing now
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
