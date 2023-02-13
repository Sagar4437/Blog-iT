from django.urls import path
from app import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',views.home, name="home"),
    path('dashboard',views.dashboard, name="dashboard"),

    # CRUD BLOG
    path('create-blog/',views.create_blog, name="create_blog"),
    path('view-blog/<str:slug>/',views.view_blog, name="view_blog"),
    path('edit-blog/<str:slug>/',views.edit_blog, name="edit_blog"),
    path('delete-blog/<str:slug>/',views.delete_blog, name="delete_blog"),
    
    path('make-featured/<str:slug>/',views.make_featured, name="make_featured"),
    path('like-blog/<str:slug>/',views.like_blog, name="like_blog"),

    path('blog-statistics',views.statistics, name="statistics"),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
