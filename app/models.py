from django.db import models
from account.models import User
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=20, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
class Blog(models.Model):
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,default=None,blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,default=None,blank=False)
    bookmarked_by = models.ManyToManyField(User, blank=True, related_name='bookmarked_blogs')
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_blogs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200,unique=True)
    short_description = models.CharField(max_length=500,blank=False,default=None)
    image = models.ImageField(null=True,blank=True,upload_to='images/')
    long_description = RichTextField()
    views = models.PositiveBigIntegerField(default=0)
    likes = models.PositiveBigIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=False)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    comment = models.TextField()
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']