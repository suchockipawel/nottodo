from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch
from nottodo.models import NotToDo, SharedNotToDo, Comment
from nottodo.tasks import send_nottodo_notifications
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime
from django.utils.timezone import make_aware
from .models import NotToDo

class NotToDoNotificationTestCase(TestCase):

    def setUp(self):
        # Set up a user for the NotToDo items
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')

    def test_send_nottodo_notifications(self):
        # Create NotToDo items, one within the notification window and one outside it
        now = timezone.now()
        nottodo_within_time = NotToDo.objects.create(
            title='Task within time',
            scheduled_start_time=now + timezone.timedelta(minutes=5),
            user=self.user
        )
        nottodo_outside_time = NotToDo.objects.create(
            title='Task outside time',
            scheduled_start_time=now + timezone.timedelta(hours=1),
            user=self.user
        )

        # Mock send_mail
        with patch('nottodo.tasks.send_mail') as mock_send_mail:
            send_nottodo_notifications()
            
            # Check that send_mail was called once
            self.assertEqual(mock_send_mail.call_count, 1)

            # Check the email details
            mock_send_mail.assert_called_with(
                'Not To Do Reminder',
                f'Remember not to do: {nottodo_within_time.title}',
                'joesaudi@hotmail.com',
                [self.user.email],
                fail_silently=False,
            )

            # Ensure no emails were sent to the out-of-time NotToDo
            # Get all the calls made to the mock
            calls = mock_send_mail.call_args_list
            # Verify that none of the calls were made for the out-of-time NotToDo
            for call in calls:
                self.assertNotIn(nottodo_outside_time.title, call[0])

#  test classes from Esther wit modifications
class NotToDoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.another_user = User.objects.create_user(username='anotheruser', password='password')
        self.nottodo = NotToDo.objects.create(
            user=self.user,
            title='Test NotToDo',
            description='Test description',
            context='Home',
            scheduled_start_time=make_aware(datetime(2024, 7, 8, 12, 0, 0)),
            scheduled_end_time=make_aware(datetime(2024, 7, 8, 13, 0, 0)),
            repeat='None'
        )
        self.shared_nottodo = SharedNotToDo.objects.create(
            nottodo=self.nottodo,
            shared_with=self.another_user
        )
    def test_update_nottodo(self):
        self.client.force_login(self.user)
        updated_title = 'Updated Test NotToDo'
        response = self.client.post(reverse('update_nottodo', kwargs={'pk': self.nottodo.pk}), {
            'title': updated_title,
            'description': 'Updated test description',
            'context': 'Work',
            'scheduled_start_time': '2024-07-09T09:00:00Z',
            'scheduled_end_time': '2024-07-09T10:00:00Z',
            'repeat': 'Daily'
        })
        self.assertEqual(response.status_code, 302)
        updated_nottodo = NotToDo.objects.get(pk=self.nottodo.pk)
        self.assertEqual(updated_nottodo.title, updated_title)
    def test_delete_nottodo(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('delete_nottodo', kwargs={'pk': self.nottodo.pk}))
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(NotToDo.DoesNotExist):
            NotToDo.objects.get(pk=self.nottodo.pk)
    def test_share_nottodo(self):
        self.client.force_login(self.user)
        shared_nottodo_exists = SharedNotToDo.objects.filter(nottodo=self.nottodo, shared_with=self.another_user).exists()
        if not shared_nottodo_exists:
            response = self.client.post(reverse('share_nottodo', kwargs={'pk': self.nottodo.pk}), {
                'shared_with': self.another_user.id,
            })
            self.assertEqual(response.status_code, 302)
        shared_nottodo_exists = SharedNotToDo.objects.filter(nottodo=self.nottodo, shared_with=self.another_user).exists()
        self.assertTrue(shared_nottodo_exists, "Shared NotToDo does not exist for this user")
    def test_add_comment(self):
        self.client.force_login(self.another_user)
        response = self.client.post(reverse('add_comment', kwargs={'shared_nottodo_id': self.shared_nottodo.pk}), {
            'text': 'Test comment',
        })
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(shared_nottodo=self.shared_nottodo, user=self.another_user)
        self.assertEqual(comment.text, 'Test comment')

    def test_copy_nottodo(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('copy_nottodo', kwargs={'pk': self.nottodo.pk}))
        self.assertEqual(response.status_code, 302)
        copied_nottodo = NotToDo.objects.last()
        expected_title = f"Copy of {self.nottodo.title}"
        self.assertEqual(copied_nottodo.title, expected_title)
        self.assertEqual(copied_nottodo.user, self.user)
        self.assertEqual(copied_nottodo.description, self.nottodo.description)
        self.assertEqual(copied_nottodo.context, self.nottodo.context)
        self.assertEqual(copied_nottodo.scheduled_start_time, self.nottodo.scheduled_start_time)
        self.assertEqual(copied_nottodo.scheduled_end_time, self.nottodo.scheduled_end_time)
        self.assertEqual(copied_nottodo.repeat, self.nottodo.repeat)
        self.assertNotEqual(copied_nottodo.id, self.nottodo.id)

class TimeZoneTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_nottodo_creation(self):
        nottodo = NotToDo.objects.create(
            user=self.user,
            title='Test NotToDo',
            scheduled_start_time=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertEqual(nottodo.scheduled_start_time.tzinfo, timezone.utc)

class TimeZoneTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_nottodo_creation(self):
        nottodo = NotToDo.objects.create(
            user=self.user,
            title='Test NotToDo',
            scheduled_start_time=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertEqual(nottodo.scheduled_start_time.tzinfo, timezone.now().tzinfo)

class NotToDoModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_string_representation(self):
        nottodo = NotToDo.objects.create(
            user=self.user,
            title='Test NotToDo',
            scheduled_start_time=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertEqual(str(nottodo), 'Test NotToDo')

    def test_default_repeat_value(self):
        nottodo = NotToDo.objects.create(
            user=self.user,
            title='Test NotToDo',
            scheduled_start_time=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertEqual(nottodo.repeat, 'None')