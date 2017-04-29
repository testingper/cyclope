# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-04-28 18:29
from __future__ import unicode_literals

import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(db_index=True, max_length=255, verbose_name='text')),
            ],
            options={
                'verbose_name': 'answer',
                'verbose_name_plural': 'answers',
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=250, verbose_name='name')),
                ('slug', autoslug.fields.AutoSlugField(blank=True, editable=True, populate_from=b'name', unique=True)),
                ('published', models.BooleanField(default=True, verbose_name='published')),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='modification date')),
                ('allow_comments', models.CharField(choices=[(b'SITE', 'default'), (b'YES', 'enabled'), (b'NO', 'disabled')], default=b'SITE', max_length=4, verbose_name='allow comments')),
                ('show_author', models.CharField(choices=[(b'AUTHOR', 'author'), (b'USER', 'user if author is empty'), (b'SITE', 'default')], default=b'SITE', help_text='Select which field to use to show as author of this content.', max_length=6, verbose_name='show author')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'poll',
                'verbose_name_plural': 'polls',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(db_index=True, max_length=255, verbose_name='text')),
                ('order', models.IntegerField(blank=True, null=True)),
                ('allow_multiple_answers', models.BooleanField(default=False, verbose_name='allow multiple answers')),
                ('poll', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='polls.Poll')),
            ],
            options={
                'ordering': ('order',),
                'verbose_name': 'question',
                'verbose_name_plural': 'questions',
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foreign_user', models.CharField(blank=True, db_index=True, max_length=60, verbose_name='foreign_user')),
                ('answers', models.ManyToManyField(to='polls.Answer', verbose_name='answers')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.Poll')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ('poll', 'user'),
                'verbose_name': 'submission',
                'verbose_name_plural': 'submissions',
            },
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.Question', verbose_name='question'),
        ),
    ]