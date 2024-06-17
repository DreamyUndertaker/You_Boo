from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ProfileForm, RatingForm, ReviewForm, UserForm
from .models import Movie, Profile, Category, Rating, Review, Like
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse

class Home(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:profile_list')
        return render(request, 'index.html')

@method_decorator(login_required, name='dispatch')
class ProfileYouView(View):
    def get(self, request, *args, **kwargs):
        profile_form = ProfileForm(instance=request.user.profile) if hasattr(request.user, 'profile') else ProfileForm()
        user_form = UserForm(instance=request.user)
        return render(request, 'profileyou.html', {'profile_form': profile_form, 'user_form': user_form})

    def post(self, request, *args, **kwargs):
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile) if hasattr(request.user, 'profile') else ProfileForm(request.POST, request.FILES)
        user_form = UserForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            user_form.save()
            return redirect('core:profile')
        return render(request, 'profileyou.html', {'profile_form': profile_form, 'user_form': user_form})

@method_decorator(login_required, name='dispatch')
class ProfileList(View):
    def get(self, request, *args, **kwargs):
        profiles = request.user.profiles.all()
        return render(request, 'profileList.html', {'profiles': profiles})

@method_decorator(login_required, name='dispatch')
class ProfileCreate(View):
    def get(self, request, *args, **kwargs):
        form = ProfileForm()
        return render(request, 'profileCreate.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST or None)
        if form.is_valid():
            profile = Profile.objects.create(**form.cleaned_data)
            if profile:
                request.user.profiles.add(profile)
                return redirect(f'/watch/{profile.uuid}')
        return render(request, 'profileCreate.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class Watch(View):
    def get(self, request, profile_id, *args, **kwargs):
        try:
            profile = Profile.objects.get(uuid=profile_id)
            if profile not in request.user.profiles.all():
                return redirect('core:profile_list')
            movies = Movie.objects.filter(age_limit=profile.age_limit)
            popular_movies = movies.filter(is_popular=True)
            categories = Category.objects.all()
            category_movies = {category.name: movies.filter(category=category) for category in categories}
            return render(request, 'movieList.html', {
                'popular_movies': popular_movies,
                'category_movies': category_movies,
            })
        except Profile.DoesNotExist:
            return redirect('core:profile_list')

@method_decorator(login_required, name='dispatch')
class ShowMovieDetail(View):
    def get(self, request, movie_id, *args, **kwargs):
        try:
            movie = Movie.objects.get(uuid=movie_id)
            return render(request, 'movieDetail.html', {'movie': movie})
        except Movie.DoesNotExist:
            return redirect('core:profile_list')

@method_decorator(login_required, name='dispatch')
class ShowMovie(View):
    def get(self, request, movie_id, *args, **kwargs):
        try:
            movie = get_object_or_404(Movie, uuid=movie_id)
            videos = movie.videos.all()
            movie_data = [{'file': video.file.url} for video in videos]
            # Логирование данных для отладки
            print("Movie Data:", movie_data)
            return render(request, 'showMovie.html', {
                'movie': movie,
                'movie_data': movie_data
            })
        except Movie.DoesNotExist:
            return redirect('core:profile_list')


@method_decorator(login_required, name='dispatch')
class MovieListView(View):
    def get(self, request, *args, **kwargs):
        popular_movies = Movie.objects.filter(is_popular=True)
        categories = Category.objects.all()
        category_movies = {category.name: Movie.objects.filter(category=category) for category in categories}
        return render(request, 'movieList.html', {
            'popular_movies': popular_movies,
            'category_movies': category_movies,
            'categories': categories
        })

@method_decorator(login_required, name='dispatch')
class CategoryListView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        return render(request, 'categoryList.html', {'categories': categories})

@method_decorator(login_required, name='dispatch')
class ShowMovieImages(TemplateView):
    template_name = 'images.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_id = self.kwargs['movie_id']
        movie = get_object_or_404(Movie, uuid=movie_id)
        context['images'] = movie.images.all()
        return context

@login_required
def add_review(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
            return redirect('core:show_det', movie_id=movie_id)
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form})

@login_required
def like_review(request, review_id):
    review = Review.objects.get(id=review_id)
    like, created = Like.objects.get_or_create(user=request.user, review=review)
    if not created:
        like.delete()
    return redirect('core:show_det', movie_id=review.movie.id)

@method_decorator(login_required, name='dispatch')
class AddRatingView(View):
    def post(self, request, movie_id):
        movie = get_object_or_404(Movie, uuid=movie_id)
        stars = int(request.POST.get('stars'))

        # Обновление или создание рейтинга
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'stars': stars}
        )
        
        return JsonResponse({'average_rating': movie.average_rating()})
    
@method_decorator(login_required, name='dispatch')
class ShowMovieDetail(View):
    def get(self, request, movie_id, *args, **kwargs):
        try:
            movie = Movie.objects.get(uuid=movie_id)
            user_rating = movie.ratings.filter(user=request.user).first()
            return render(request, 'movieDetail.html', {
                'movie': movie,
                'average_rating': movie.average_rating(),
                'user_rating': user_rating.stars if user_rating else 0
            })
        except Movie.DoesNotExist:
            return redirect('core:profile_list')
        
def show_movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, uuid=movie_id)
    reviews = movie.reviews.all()[:3]
    review_form = ReviewForm()
    return render(request, 'movieDetail.html', {'movie': movie, 'reviews': reviews, 'review_form': review_form})

def show_all_reviews(request, movie_id):
    movie = get_object_or_404(Movie, uuid=movie_id)
    reviews = movie.reviews.all()
    review_form = ReviewForm()
    return render(request, 'review.html', {'movie': movie, 'reviews': reviews, 'review_form': review_form})

@login_required
def add_review(request, movie_id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, uuid=movie_id)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            return redirect('core:show_det', movie_id=movie_id)
    return redirect('core:show_det', movie_id=movie_id)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('core:show_det', movie_id=review.movie.uuid)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('core:show_det', movie_id=review.movie.uuid)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'edit_review.html', {'form': form, 'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user:
        review.delete()
    return redirect('core:show_det', movie_id=review.movie.uuid)

@login_required
def like_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.likes.filter(id=request.user.id).exists():
        review.likes.remove(request.user)
    else:
        review.likes.add(request.user)
    return JsonResponse({'total_likes': review.total_likes()})


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, uuid=movie_id)
    reviews = movie.reviews.all()
    review_form = ReviewForm()

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            return redirect('core:movie_detail', movie_id=movie_id)

    return render(request, 'movie_detail.html', {
        'movie': movie,
        'reviews': reviews,
        'review_form': review_form
    })

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'profile.html')

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен.')
            return redirect('core:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки.')
        return render(request, 'profile.html', {'user_form': user_form})

@method_decorator(login_required, name='dispatch')
class SubscriptionManagementView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'subscription_management.html')
    
@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        return redirect('core:profile')
    return render(request, 'profile.html')

def search(request):
    query = request.GET.get('query', '')
    if query:
        movies = Movie.objects.filter(title__icontains=query)
    else:
        movies = Movie.objects.none()

    return render(request, 'search_results.html', {'movies': movies, 'query': query})