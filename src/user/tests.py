from django.urls import reverse_lazy
from rest_framework.test import APITestCase
from .models import User


class TestUser(APITestCase):

    url = reverse_lazy("user-list")
    token_url = reverse_lazy("token_obtain_pair")

    def token_test(self):
        user_test = User.objects.create(
            username="Test_User",
            password="Test_Password",
            age=16
        )
        response = self.client.post(
            self.token_url, body={
                "username": user_test.username,
                "password": user_test.password
            }
        )
        user_token = response.json()["access"]
        self.assertEqual(response.status_code, 200)
        all_users_raw = self.client.get(self.url, headers={
            "Authorization": "Bearer " + user_token
        })
        all_users = all_users_raw.json()
        expected = {
            "username": user_test.username
        }
        self.assertEqual(all_users, expected)
