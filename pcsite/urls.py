from django.contrib import admin
from django.urls import path
from configurator import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('save/', views.save_build, name='save_build'), 
    path('builds/', views.view_builds, name='view_builds'), 
]