from django.contrib import admin
from .models import CustomUser, Profile, Movie, Video, Category, Image

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Movie)
admin.site.register(Video)
admin.site.register(Image)
admin.site.register(Category)
