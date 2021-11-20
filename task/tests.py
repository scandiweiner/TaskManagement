import datetime
import json
from datetime import timedelta

import pytz
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Task
from . import errors

User = get_user_model()


class TestTask(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='yana_test',
            first_name='Yana',
            last_name='Weiner',
        )
        self.mock_date = datetime.datetime(2021, 1, 1, 10, 10, 10, tzinfo=pytz.UTC)
        self.task = Task.objects.create(
            description='Create API for task management',
        )

    def test_checkin_task(self):
        data = {
            'user_id': self.user.id,
            'checkin_date': self.mock_date,
        }
        response = self.client.post(
            reverse('checkin', args=[self.task.id]),
            data=data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        task = Task.objects.get(user_id=1)
        self.assertEqual(task.checkin_date, self.mock_date)
        self.assertEqual(task.description, 'Create API for task management')
        self.assertIsNone(task.checkout_date)

    def test_cannot_checkin_task_if_user_has_another_task(self):
        # assign user to task and checkin
        self.task.user = self.user
        self.task.checkin_date = self.mock_date
        self.task.save(update_fields=['user', 'checkin_date'])

        data = {
            'user_id': self.user.id,
            'checkin_date': self.mock_date,
            'description': 'Resolve bugs in a different feature',
        }
        response = self.client.post(
            reverse('checkin', args=[self.task.id]),
            data=data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['error'], errors.USER_ALREADY_HAS_AN_OPEN_TASK)
        self.assertEqual(Task.objects.all().count(), 1)

    def test_checkout_task(self):
        task = Task.objects.create(
            user=self.user,
            checkin_date=self.mock_date,
            description='Create API for task management',
        )
        data = {
            'checkout_date': self.mock_date + timedelta(hours=2),
        }
        response = self.client.post(
            reverse('checkout', args=[task.id]),
            data=data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        task.refresh_from_db()
        self.assertEqual(task.checkout_date, self.mock_date + timedelta(hours=2))

    def test_report(self):
        first_task = Task.objects.create(
            user=self.user,
            checkin_date=self.mock_date,
            checkout_date=self.mock_date + timedelta(hours=2),
            description='Create API for task management',
        )

        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode('utf-8'))
        self.assertIsNotNone(data)
        self.assertEqual(len(data[self.user.username]), 1)
        self.assertEqual(data[self.user.username][0], f'{first_task.description}: 2 hours')

        # check that task with no checkout date isn't showing up in report
        another_task = Task.objects.create(
            user=self.user,
            checkin_date=self.mock_date + timedelta(hours=3),
            description='Add tests for Task API',
        )
        self.client.get(reverse('report'))
        self.assertEqual(len(data[self.user.username]), 1)

        # check it adds to report once checkout date is added
        another_task.checkout_date = self.mock_date + timedelta(hours=4)
        another_task.save(update_fields=['checkout_date'])
        another_task.refresh_from_db()

        response = self.client.get(reverse('report'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertIsNotNone(data)
        self.assertEqual(len(data[self.user.username]), 2)
        self.assertEqual(data[self.user.username][1], f'{another_task.description}: 1 hours')
