from django.contrib import admin
from .models import Movie, Collection

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'genres')
    search_fields = ('title', 'genres')
    ordering = ('title',)
    list_filter = ('genres',)

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'get_movie_count', 'favourite_genres')
    search_fields = ('title', 'description')
    ordering = ('title',)
    list_filter = ('movies',)

    def get_movie_count(self, obj):
        return obj.movies.count()
    get_movie_count.short_description = 'Number of Movies'
