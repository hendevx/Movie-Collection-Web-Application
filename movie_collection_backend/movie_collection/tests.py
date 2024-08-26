from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Movie, Collection

class UserTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.username = 'pratik'
        self.password = 'pratik'
        self.user = User.objects.create_user(username=self.username, password=self.password)
    
    def test_user_registration(self):
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
    
    def test_user_login(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
    
    def test_user_login_failure(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)


class CollectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.collection_list_url = reverse('collection-list')
        self.collection_detail_url = lambda uuid: reverse('collection-detail', args=[uuid])
        
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.token = RefreshToken.for_user(self.user).access_token
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'
        
        self.movie1 = Movie.objects.create(
            title='Movie 1',
            description='Description 1',
            genres='Action,Adventure'
        )
        self.movie2 = Movie.objects.create(
            title='Movie 2',
            description='Description 2',
            genres='Action,Comedy'
        )
        self.collection = Collection.objects.create(
            title='Collection 1',
            description='Description of collection'
        )
        self.collection.movies.add(self.movie1, self.movie2)
    
    # Failed
    def test_create_collection(self):
        response = self.client.post(self.collection_list_url, {
            'title': 'New Collection',
            'description': 'Description of new collection',
            'movies': [
                {
                    'title': 'Movie 1',
                    'description': 'Description 1',
                    'genres': 'Action,Adventure'
                },
                {
                    'title': 'Movie 2',
                    'description': 'Description 2',
                    'genres': 'Action,Comedy'
                }
            ]
        }, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('collection_uuid', response.data)


    def test_list_collections(self):
        response = self.client.get(self.collection_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('collections', response.data['data'])
    
    def test_get_collection_detail(self):
        response = self.client.get(self.collection_detail_url(self.collection.uuid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.collection.title)
    
    # Failed
    def test_update_collection(self):
        response = self.client.put(self.collection_detail_url(self.collection.uuid), {
            'title': 'Updated Collection Title',
            'description': 'Updated description',
            'movies': [
                {
                    'title': 'Movie 1',
                    'description': 'Description 1',
                    'genres': 'Action,Adventure'
                }
            ]
        }, content_type='application/json') 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Collection Title')


    
    def test_delete_collection(self):
        response = self.client.delete(self.collection_detail_url(self.collection.uuid))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Collection.objects.count(), 0)


class RequestCountTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.request_count_url = reverse('request_count')
        self.reset_request_count_url = reverse('reset_request_count')
        
        self.username = 'admin'
        self.password = 'admin'
        self.user = User.objects.create_superuser(username=self.username, password=self.password)
        self.token = RefreshToken.for_user(self.user).access_token
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'
    
    def test_request_count(self):
        response = self.client.get(self.request_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('requests', response.data)
    
    def test_reset_request_count(self):
        response = self.client.post(self.reset_request_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'request count reset successfully')


class MovieTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.fetch_movies_url = reverse('movie-list')
    
    def test_fetch_movies(self):
        response = self.client.get(self.fetch_movies_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)
