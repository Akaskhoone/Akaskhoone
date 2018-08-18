# Generated by Django 2.1 on 2018-08-18 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True, null=True, verbose_name='biography'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='followers',
            field=models.ManyToManyField(blank=True, null=True, related_name='user_followers', to='users.Profile'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='followings',
            field=models.ManyToManyField(blank=True, null=True, related_name='user_followings', to='users.Profile'),
        ),
    ]
