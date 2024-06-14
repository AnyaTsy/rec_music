import unittest
from unittest.mock import patch
from auth import authenticate_user, register_user
from locust import HttpUser, task, between

#перевіркf реагування системи на перевантаження
class StressTest(HttpUser):
    wait_time = between(1, 2)  # Час очікування між запитами

    @task
    def load_profile(self):
        self.client.post("/login", {"username": "test_user", "password": "test_password"})
        self.client.get("/profile")

class TestAuthentication(unittest.TestCase):

    @patch('auth.sqlite3.connect')
    def test_login_successful(self, mock_connect):
        """Тест успішного входу в систему з моком бази даних"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = ('test_user', 'test_password')

        result = authenticate_user('test_user', 'test_password')
        self.assertTrue(result)

    @patch('auth.sqlite3.connect')
    def test_login_failure(self, mock_connect):
        """Тест входу з неправильним паролем з моком бази даних"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = None

        result = authenticate_user('test_user', 'wrong_password')
        self.assertFalse(result)

    @patch('auth.sqlite3.connect')
    def test_registration(self, mock_connect):
        """Тест реєстрації нового користувача з перевіркою викликів до БД"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = None

        result = register_user('new_user', 'new_password')
        self.assertEqual(result, "Registered successfully")
        mock_cursor.execute.assert_called_with("INSERT INTO users (username, password) VALUES (?, ?)", ('new_user', 'new_password'))
    

    def test_recommendations_with_empty_input(self):
        """Тест рекомендацій при відсутності вхідних даних"""
        recommendations = recommend_songs([], self.mock_data, ['name', 'artists', 'id'], MagicMock())
        self.assertEqual(recommendations, [])

    def test_recommendations_with_valid_input(self):
        """Тест рекомендацій при наявності вхідних даних"""
        mock_pipeline = MagicMock()
        mock_pipeline.steps = [('scaler', MagicMock()), ('kmeans', MagicMock())]
        recommendations = recommend_songs([{'name': 'Song1'}], self.mock_data, ['name', 'artists', 'id'], mock_pipeline, 1)
        self.assertGreater(len(recommendations), 0)
    
    def setUp(self):
        # URL веб-додатка
        self.base_url = "http://yourapp.com"
        # Стандартні дані для входу
        self.auth_payload = {"username": "existing_user", "password": "old_password"}

        # Спочатку виконуємо вхід, щоб отримати токен аутентифікації або сесійний ключ
        response = requests.post(f"{self.base_url}/login", data=self.auth_payload)
        self.token = response.json().get('token')

    def test_update_username(self):
        # Дані для оновлення профілю
        update_payload = {"username": "updated_user"}
        headers = {'Authorization': f'Bearer {self.token}'}

        # Виконуємо запит на оновлення
        response = requests.post(f"{self.base_url}/update_profile", headers=headers, data=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Profile updated successfully", response.text)


    