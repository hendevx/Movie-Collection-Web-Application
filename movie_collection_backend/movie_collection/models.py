from django.db import models
from collections import Counter
import uuid

class Movie(models.Model):
    """Model representing a movie."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    genres = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title

class Collection(models.Model):
    """Model representing a collection of movies."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    movies = models.ManyToManyField(Movie, related_name='collections')

    def __str__(self):
        return self.title

    @property
    def favourite_genres(self):
        """Returns the most common genres in the collection."""

        all_genres = []
        for movie in self.movies.all():
            all_genres.extend(movie.genres.split(','))
        
        most_common_genres = Counter(all_genres).most_common(3)
        return ','.join([genre for genre, _ in most_common_genres])
