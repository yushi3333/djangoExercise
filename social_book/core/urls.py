from django.urls import path
from . import views

urlpatterns =[
    path('', views.index, name = "index"),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name = 'signin'),
    path('logout', views.logout,name="logouts"),
    path('settings',views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('like_post', views.like_post, name="like_post"),
    path('profile/<str:username>', views.profile, name = "profile"),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('comment/<uuid:post_id>/', views.add_comment, name='add_comment'),
    path('delete/<uuid:post_id>/', views.delete_post, name='delete_post'),
]