# Generated by Django 5.0.1 on 2024-02-11 07:35

import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_alter_product_specifications_alter_user_avatar_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, default='user_avatars/avatar_default.jpeg', force_format='JPEG', keep_meta=True, quality=75, scale=0.5, size=[168, 168], upload_to='user_avatars/'),
        ),
        migrations.AlterField(
            model_name='user',
            name='banner',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, default='user_avatars/banner_default.jpg', force_format='JPEG', keep_meta=True, quality=75, scale=0.5, size=[1198, 124], upload_to='user_banners/'),
        ),
    ]
