# Generated by Django 2.2.7 on 2020-02-12 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tempAPP', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': '标签',
                'verbose_name_plural': '标签',
            },
        ),
        migrations.AddField(
            model_name='customerfollowup',
            name='tag',
            field=models.ManyToManyField(to='tempAPP.Tag'),
        ),
    ]
