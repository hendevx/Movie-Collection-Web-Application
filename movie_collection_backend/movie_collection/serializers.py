from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Collection, Movie


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password',)
        
    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['uuid', 'title', 'description', 'genres']

class CollectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['title', 'uuid', 'description']


class CollectionSerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True)

    class Meta:
        model = Collection
        fields = ['title', 'description', 'movies']

    def create(self, validated_data):
        movies_data = validated_data.pop('movies', [])

        collection = Collection.objects.create(**validated_data)

        for movie_data in movies_data:
            movie, created = Movie.objects.get_or_create(
                title=movie_data['title'],
                defaults={
                    'description': movie_data['description'],
                    'genres': movie_data['genres']
                }
            )
            collection.movies.add(movie)

        return collection

    def update(self, instance, validated_data):
        movies_data = validated_data.pop('movies', [])

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        instance.movies.clear()
        
        for movie_data in movies_data:
            movie, created = Movie.objects.get_or_create(
                title=movie_data['title'],
                defaults={
                    'description': movie_data['description'],
                    'genres': movie_data['genres']
                }
            )
            instance.movies.add(movie)

        return instance
