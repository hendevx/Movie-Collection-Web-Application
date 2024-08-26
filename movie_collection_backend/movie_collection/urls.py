from django.urls import path
from .views import (
    RequestCountView,
    UserRegistrationView,
    UserLoginView,
    ExpiredTokenRefreshView,
    LogoutView,
    MovieListView,
    CollectionListView,
    CollectionDetailView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("refresh/", ExpiredTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("movies/", MovieListView.as_view(), name="movie-list"),
    path('collection/', CollectionListView.as_view(), name='collection-list'),
    path('collection/<uuid:collection_uuid>/', CollectionDetailView.as_view(), name='collection-detail'),
    path('request-count/', RequestCountView.as_view(), name='request_count'),
    path('request-count/reset/', RequestCountView.as_view(), name='reset_request_count'),
]
