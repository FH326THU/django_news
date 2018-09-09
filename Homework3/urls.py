"""Homework3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from news import views

hander404 = "news.views.notfound"

urlpatterns = [
    # path('django_admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('admin/', views.admin, name='admin'),
    path('admin_recover/', views.admin_recover, name='admin_recover'),
    path('news/', views.news, name='news'),
    path('news/<int:id>', views.news, name='news'),
    path('news_content/<int:id>', views.news_content, name='news_content'),
    path('del/<int:id>', views.del_news, name='del_news'),
    path('del/', views.del_many, name='del_many'),
    path('recover/<int:id>', views.recover_news, name='recover_news'),
    path('recover/', views.recover_many, name='recover_many'),
    path('logout/', views.logout, name='logout'),
    path('getnew/', views.getnew, name='getnew'),
    path('query/<str:s>', views.query, name='query'),
    path('query_title/<str:s>', views.query_title, name='query_title'),
]
