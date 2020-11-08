# Generated by Django 2.2.6 on 2020-11-08 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20201105_1618'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_item'),
        ),
    ]