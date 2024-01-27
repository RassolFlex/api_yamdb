import json
from os import listdir
from pathlib import Path

import pandas
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        csv_data = []
        for file in listdir('static/data/'):
            dataframe = pandas.read_csv(Path(f'static/data/{file}'))
            json_file = dataframe.to_json(orient='records')
            parsed = json.loads(json_file)
            for index, item in enumerate(parsed):
                model_dict = dict()
                model_dict['model'] = f'reviews.{Path(file).stem}'
                pk = parsed[index].pop('id')
                model_dict['pk'] = pk
                model_dict['fields'] = parsed[index]
                csv_data.append(model_dict)
        with open('data.json', 'w') as f:
            json.dump(csv_data, f, ensure_ascii=False, indent=4)
