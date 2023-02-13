from django.db import models
from account.models import User
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=20, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class Blog(models.Model):
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,default=None,blank=False)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE,default=None,blank=False)
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
