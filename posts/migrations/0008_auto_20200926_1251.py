# Generated by Django 2.2.9 on 2020-09-26 05:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0007_group_posts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='posts',
        ),
        migrations.AddField(
            model_name='group',
            name='posts',
            field=models.ManyToManyField(blank=True, null=True, related_name='group_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]
