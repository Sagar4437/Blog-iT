# Generated by Django 4.1.6 on 2023-02-24 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_user_about'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_creator',
            field=models.BooleanField(default=False),
        ),
    ]
