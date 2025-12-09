from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Event

User = get_user_model()

class EventAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1', password='pass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_event(self):
        url = reverse('events-list')
        data = {
            'title': 'Test event',
            'description': 'desc',
            'location': 'City',
            'start_time': '2030-01-01T10:00:00Z',
            'end_time': '2030-01-01T12:00:00Z',
            'is_public': True
        }
        resp = self.client.post(url, data, format='json')
        assert resp.status_code == 201
        assert Event.objects.count() == 1
        assert Event.objects.first().organizer == self.user
