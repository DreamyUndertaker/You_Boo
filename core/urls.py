from django.urls import path
from .views import (
    Home, ProfileYouView, ProfileList, ProfileCreate, Watch, ShowMovieDetail,
    ShowMovie, MovieListView, CategoryListView, ShowMovieImages, AddRatingView,
    add_review, like_review, show_movie_detail, show_all_reviews, edit_review, delete_review,
    ProfileView, SubscriptionManagementView, search
)
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'core'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('profile/', ProfileYouView.as_view(), name='profileyou'),
    path('profile/list/', ProfileList.as_view(), name='profile_list'),
    path('profile/create/', ProfileCreate.as_view(), name='profile_create'),
    path('watch/<uuid:profile_id>/', Watch.as_view(), name='watch'),
    path('movie/<uuid:movie_id>/', show_movie_detail, name='show_det'),
    path('movie/<uuid:movie_id>/reviews/', show_all_reviews, name='all_reviews'),
    path('play/<uuid:movie_id>/', ShowMovie.as_view(), name='play'),
    path('movies/', MovieListView.as_view(), name='movie_list'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('movie/<uuid:movie_id>/images/', ShowMovieImages.as_view(), name='images'),
    path('add_rating/<uuid:movie_id>/', AddRatingView.as_view(), name='add_rating'),
    path('add_review/<uuid:movie_id>/', add_review, name='add_review'),
    path('edit_review/<int:review_id>/', edit_review, name='edit_review'),
    path('delete_review/<int:review_id>/', delete_review, name='delete_review'),
    path('like_review/<int:review_id>/', like_review, name='like_review'),
    path('movies/<uuid:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movies/<uuid:movie_id>/add_review/', views.add_review, name='add_review'),
    path('profile/view/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileView.as_view(), name='update_user_info'),
    path('subscription/management/', SubscriptionManagementView.as_view(), name='subscription_management'),
    path('search/', search, name='search'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
