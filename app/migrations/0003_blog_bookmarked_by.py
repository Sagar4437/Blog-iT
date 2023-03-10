# Generated by Django 4.1.6 on 2023-02-22 12:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0002_alter_blog_options_alter_blog_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='bookmarked_by',
            field=models.ManyToManyField(blank=True, related_name='bookmarked_blogs', to=settings.AUTH_USER_MODEL),
        ),
    ]
