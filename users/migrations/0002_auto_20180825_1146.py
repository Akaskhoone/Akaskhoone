# Generated by Django 2.1 on 2018-08-25 11:46

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=30, validators=[users.models.NameValidator], verbose_name='first name'),
        ),
    ]
