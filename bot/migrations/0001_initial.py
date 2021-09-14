# Generated by Django 3.2.3 on 2021-05-23 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='messagelog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupID', models.CharField(default='', max_length=50)),
                ('userID', models.CharField(default='', max_length=50)),
                ('message', models.CharField(blank=True, default='', max_length=255)),
                ('message_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
