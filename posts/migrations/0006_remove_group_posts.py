# Generated by Django 2.2.9 on 2020-09-26 05:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20200926_1217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='posts',
        ),
    ]