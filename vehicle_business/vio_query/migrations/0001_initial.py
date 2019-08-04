# Generated by Django 2.2.1 on 2019-05-20 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=50)),
                ('authority', models.IntegerField(blank=True, default=1, null=True)),
                ('comments', models.CharField(blank=True, max_length=200, null=True)),
                ('is_delete', models.BooleanField(default=False)),
            ],
        ),
    ]