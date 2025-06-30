from django.urls import reverse_lazy
from rest_framework.test import APITestCase
from rest_framework import status
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

    def test_user_can_delete_own_profile(self):
        """
        Test que un utilisateur peut supprimer son propre profil
        """
        # Créer un utilisateur
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            age=25
        )
        
        # Obtenir le token d'authentification
        response = self.client.post(
            self.token_url,
            data={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        self.assertEqual(response.status_code, 200)
        token = response.json()["access"]
        
        # URL pour supprimer le profil
        delete_url = reverse_lazy("user-detail", kwargs={"pk": user.pk})
        
        # Tenter de supprimer le profil
        response = self.client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Vérifier que la suppression a réussi
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Vérifier que l'utilisateur n'existe plus
        self.assertFalse(User.objects.filter(pk=user.pk).exists())

    def test_user_cannot_delete_other_profile(self):
        """
        Test qu'un utilisateur ne peut pas supprimer le profil d'un autre utilisateur
        """
        # Créer deux utilisateurs
        user1 = User.objects.create_user(
            username="user1",
            password="pass123",
            age=25
        )
        user2 = User.objects.create_user(
            username="user2", 
            password="pass456",
            age=30
        )
        
        # Obtenir le token pour user1
        response = self.client.post(
            self.token_url,
            data={
                "username": "user1",
                "password": "pass123"
            }
        )
        self.assertEqual(response.status_code, 200)
        token = response.json()["access"]
        
        # URL pour supprimer le profil de user2
        delete_url = reverse_lazy("user-detail", kwargs={"pk": user2.pk})
        
        # Tenter de supprimer le profil de user2 avec le token de user1
        response = self.client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Vérifier que la suppression est refusée
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Vérifier que user2 existe toujours
        self.assertTrue(User.objects.filter(pk=user2.pk).exists())
