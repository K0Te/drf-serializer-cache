"""Currencies application data model."""

from django.db import models


class User(models.Model):
    id = models.AutoField('Identifier', primary_key=True)
    name = models.CharField('Name', max_length=70)


class FilmCategory(models.Model):
    id = models.AutoField('Identifier', primary_key=True)
    name = models.CharField('Name', max_length=70)
    parent_category = models.ForeignKey('FilmCategory',
                                        null=True, default=None)


class Film(models.Model):
    id = models.AutoField('Identifier', primary_key=True)
    year = models.IntegerField('Year')
    name = models.CharField('Name', max_length=70)
    uploaded_by = models.ForeignKey(User)
    category = models.ForeignKey(FilmCategory)
