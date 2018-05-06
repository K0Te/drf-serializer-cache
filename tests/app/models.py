from django.db import models


class User(models.Model):
    id = models.AutoField('Identifier', primary_key=True)
    name = models.CharField('Name', max_length=70)
    email = models.EmailField()


class FilmCategory(models.Model):
    id = models.AutoField('Identifier', primary_key=True)
    name = models.CharField('Name', max_length=70)
    parent_category = models.ForeignKey('FilmCategory',
                                        null=True,
                                        default=None,
                                        on_delete=models.PROTECT)


class Film(models.Model):
    id = models.AutoField('Identifier', primary_key=True)
    year = models.IntegerField('Year')
    name = models.CharField('Name', max_length=70)
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT)
    category = models.ForeignKey(FilmCategory, on_delete=models.PROTECT)


class CategoryHierarchy:
    def __init__(self, category, films=None, categories=None):
        self.category = category
        if films is None:
            self.films = []
        else:
            self.films = films
        if categories is None:
            self.categories = []
        else:
            self.categories = categories
