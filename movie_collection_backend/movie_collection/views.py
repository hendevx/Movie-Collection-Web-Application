from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from urllib.parse import urlparse, urlunparse
from .utils import fetch_movies
from .models import Collection
from .serializers import UserSerializer, CollectionSerializer, CollectionListSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                
                response = Response({
                    'message': f'{user.username}\'s account is registered!',
                    'access_token': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)

                response.set_cookie('access', str(refresh.access_token), httponly=True, samesite='Lax')
                response.set_cookie('refresh', str(refresh), httponly=True, samesite='Lax')
                
                return response
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            refresh_token = response.data['refresh']
            access_token = response.data['access']

            if not refresh_token or not access_token:
                raise ValueError("Tokens are missing from response data")
            
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response_data = {
                'username': request.data["username"],
                'message': f'{request.data["username"]} is logged in',
                'access_token': access_token,
                'refresh_token': str(refresh)
            }

            response.set_cookie('refresh', str(refresh), httponly=True, samesite='Lax')
            response.set_cookie('access', access_token, httponly=True, samesite='Lax')
            
            response.data = response_data
            
            return response

        except Exception as e:
            print(f"Error in UserLoginView: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class ExpiredTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh')

            if not refresh_token:
                return JsonResponse({'error': 'Missing refresh token in cookie'}, status=400)

            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)

            if response.status_code == status.HTTP_200_OK:
                access_token = response.data.get('access')
                refresh_token = response.data.get('refresh')

                if access_token:
                    response.set_cookie('access', access_token, httponly=True, samesite='Lax')
                if refresh_token:
                    response.set_cookie('refresh', refresh_token, httponly=True, samesite='Lax')

                response_data = {'access_token': access_token}
                return Response(response_data, status=status.HTTP_200_OK)

            return response

        except TokenError as e:
            return JsonResponse({'Token error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'Unexpected error': str(e)}, status=500)


class LogoutView(APIView):
    def post(self, request):
        try:
            response = JsonResponse({'message': 'Logout successful'}, status=status.HTTP_200_OK)
            
            response.delete_cookie('access')
            response.delete_cookie('refresh')
            
            return response
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MovieListView(APIView):
    def get(self, request):
        page = int(request.GET.get('page', 1))
        movies_data = fetch_movies(page)
        full_url = request.build_absolute_uri()
        parsed_url = urlparse(full_url)
        url_without_query = urlunparse(parsed_url._replace(query=''))
        
        if movies_data:
            total_pages = (movies_data['count'] + 9) // 10
            next_page = page + 1 if page < total_pages else None
            previous_page = page - 1 if page > 1 else None
            
            response_data = {
                'count': movies_data['count'],
                'next': url_without_query + f'?page={next_page}' if next_page else None,
                'previous': url_without_query + f'?page={previous_page}' if previous_page else None,
                'results': movies_data['data']
            }
            return Response(response_data)
        
        return Response({'error': 'Failed to fetch movies'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CollectionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            collections = Collection.objects.all()
            serializer = CollectionListSerializer(collections, many=True)
            unique_favourite_genres = set()

            for collection in collections:
                genres = (genre.strip() for genre in collection.favourite_genres.split(',') if genre.strip())
                unique_favourite_genres.update(genres)

            sorted_favourite_genres = sorted(unique_favourite_genres)

            response = {
                "is_success": True,
                "data": {
                    "collections": serializer.data,
                    "favourite_genres": sorted_favourite_genres
                }
            }

            return Response(response)
        
        except Exception as e:
            print(f"An error occurred while processing the request: {str(e)}")

            return Response(
                {"is_success": False, "message": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            collection = serializer.save()
            return Response({'collection_uuid': str(collection.uuid)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, collection_uuid):
        try:
            collection = Collection.objects.get(uuid=collection_uuid)
        except Collection.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CollectionSerializer(collection)
        return Response(serializer.data)

    def put(self, request, collection_uuid):
        try:
            collection = Collection.objects.get(uuid=collection_uuid)
        except Collection.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CollectionSerializer(collection, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, collection_uuid):
        try:
            collection = Collection.objects.get(uuid=collection_uuid)
        except Collection.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        collection.delete()
        return Response({'collection_uuid': str(collection.uuid)+' deleted'}, status=status.HTTP_204_NO_CONTENT)


class RequestCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        count = cache.get('request_count', 0)
        return Response({'requests': count})

    def post(self, request):
        cache.set('request_count', 0)
        return Response({'message': 'request count reset successfully'})
    