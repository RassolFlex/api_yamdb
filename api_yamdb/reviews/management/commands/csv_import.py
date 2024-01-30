from pathlib import Path
import csv
from sqlite3 import IntegrityError

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.utils import IntegrityError

from reviews.constants import APP_LABEL


class FileOpenException(Exception):
    """Вызов исключения при некорректном открытии файла."""
    pass


class Command(BaseCommand):
    def handle(self, **options):
        files = [
            'apiuser.csv',
            'category.csv',
            'genre.csv',
            'title.csv',
            'title_genre.csv',
            'review.csv',
            'comment.csv',
        ]
        for file in files:
            model_name = Path(file).stem
            model_class = apps.get_model(APP_LABEL, model_name)
            try:
                with open(f'static/data/{file}', newline='') as f:
                    dataframe = csv.DictReader(f)
                    for row in dataframe:
                        try:
                            model_class.objects.create(**row)
                        except IntegrityError:
                            self.stdout.write(
                                f'Object {model_name} ID:'
                                f'{row.get('id')} already exists'
                            )
                            continue
                    self.stdout.write(
                        f'Data import finished for model: {model_name}'
                    )
            except FileOpenException as error:
                self.stdout.write(f'Ошибка при открытии файла: {error}')
                continue
