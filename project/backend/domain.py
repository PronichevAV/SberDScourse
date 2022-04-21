import asyncio
import concurrent.futures
import random
import re
from functools import partial

import plotly
import plotly.express as px

import nltk
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pymorphy2 import MorphAnalyzer

from db.db_utils import get_raw_data_from_db, write_raw_data_to_db, is_table_exist, \
    write_clear_data_to_db, get_clear_data_from_db
from models.tf_idf_model.tf_idf_model import ModelTfIdf
from models.fasttext_model.fasttext_model import ModelFastText

nltk.download('stopwords')
nltk.download('punkt')


class Domain:
    def __init__(self, config):
        self.config = config
        self.data_pipeline()
        self.models = {'TF-IDF': ModelTfIdf(db_path=self.config.db_path),
                       'FastText': ModelFastText(db_path=self.config.db_path,
                                                 model_path=self.config.model_path)}
        self.data = get_clear_data_from_db(db_path=self.config.db_path)

    def predict(self, raw_query: str):
        query = self.clean_text(raw_query)
        for model_name, model in self.models.items():
            self.data[model_name] = model.predict(query)
        self.data['score'] = np.mean(self.data[[model for model in self.models.keys()]], axis=1)
        result = []
        for row in self.data.sort_values(by='score', ascending=False).head(10).iterrows():
            iter_result = {
                'id': row[1]['vacancy_id'],
                'url': row[1]['vacancy_url'],
                'title': row[1]['vacancy_name'].capitalize(),
                'company': row[1]['company_name'],
                'description': row[1]['description'],
                'score': round(row[1]['score'], 3)
            }
            result.append(iter_result)
        return result

    def data_pipeline(self):
        if not is_table_exist(table_name='data_lake', db_path=self.config.db_path) or self.config.need_db_update:
            items = self.get_raw_data(vacancy_count=1000, chunk_size=100)
            write_raw_data_to_db(items=items, db_path=self.config.db_path)
        if not is_table_exist(table_name='data_mart', db_path=self.config.db_path) or self.config.need_db_update:
            items = get_raw_data_from_db(db_path=self.config.db_path)
            data = self.prepare_data(items=items)
            write_clear_data_to_db(data=data, table='data_mart', db_path=self.config.db_path)

    @staticmethod
    def clean_text(text: str, stop_words: list = stopwords.words('english') + stopwords.words('russian')) -> str:
        text_without_html = BeautifulSoup(text, features="html.parser").get_text()
        lower_text = text_without_html.lower()
        result_text = re.sub('[^а-яa-z]+', ' ', lower_text)
        token_text = word_tokenize(result_text)
        cleaned_token_text = [word for word in token_text if word not in stop_words]
        lemmatizer = MorphAnalyzer()
        result_token_text = [lemmatizer.parse(word)[0].normal_form for word in cleaned_token_text]
        merged_token_text = ' '.join(result_token_text)
        return merged_token_text

    @staticmethod
    async def get_chunk_data(chunk_size: int = 10):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            valid_ids = []
            valid_data = []
            loop = asyncio.get_event_loop()
            offsets = [random.randrange(1, 999, 1) for _ in range(chunk_size)]
            url = 'http://opendata.trudvsem.ru/api/v1/vacancies'
            futures = [loop.run_in_executor(executor,
                                            partial(requests.get,
                                                    url=url + f'?offset={offset}&limit=10',
                                                    verify=False)) for offset in offsets]
            for response in await asyncio.gather(*futures):
                if response.status_code == 200:
                    json_data = response.json()
                    valid_ids.extend([element['vacancy']['id'] for element in json_data['results']['vacancies']])
                    valid_data.extend(json_data['results']['vacancies'])
            return valid_ids, valid_data

    def get_raw_data(self, vacancy_count: int = 100, chunk_size: int = 10):
        ids = []
        data = []
        while len(set(ids)) < vacancy_count:
            loop = asyncio.get_event_loop()
            chunk_ids, chunk_data = loop.run_until_complete(self.get_chunk_data(chunk_size=chunk_size))
            ids += chunk_ids
            data += chunk_data
        return data

    def prepare_data(self, items: list) -> pd.DataFrame:
        data = pd.DataFrame({'data': items})
        data['vacancy_id'] = data['data'].apply(lambda x: x['vacancy'].get('id', 'unknown'))
        data['vacancy_name'] = data['data'].apply(lambda x: x['vacancy'].get('job-name', 'Неизвестная вакансия'))
        data['vacancy_url'] = data['data'].apply(lambda x: x['vacancy'].get('vac_url', 'https://trudvsem.ru'))
        data['company_inn'] = data['data'].apply(lambda x: x['vacancy'].get('company', {}).get('inn'))
        data['company_name'] = data['data'].apply(lambda x: x['vacancy'].get('company', {}).get('name'))
        data['lng'] = data['data'].apply(lambda x: x['vacancy'].get('addresses', {}).get('address', [{}])[0].get('lng', 0))
        data['lat'] = data['data'].apply(lambda x: x['vacancy'].get('addresses', {}).get('address', [{}])[0].get('lat', 0))
        data['location'] = data['data'].apply(lambda x: x['vacancy'].get('addresses', {}).get('address', [{}])[0].get('location', 0))
        data['description'] = data['data'].apply(lambda x: x['vacancy'].get('duty', 'Полное описание отсутствует'))
        data['merged_text'] = data['data'].apply(lambda x: ' '.join([x['vacancy'].get('job-name', ''),
                                                                     x['vacancy'].get('duty', ''),
                                                                     x['vacancy'].get('shedule', ''),
                                                                     x['vacancy'].get('category', {}).get(
                                                                         'specialisation',
                                                                         ''),
                                                                     x['vacancy'].get('requirement', {}).get(
                                                                         'education',
                                                                         ''),
                                                                     x['vacancy'].get('requirement', {}).get(
                                                                         'qualification', '')
                                                                     ])
                                                 )
        data['tokenized_description'] = data['merged_text'].apply(lambda x: self.clean_text(text=x))
        data.drop(columns=['data', 'merged_text'], inplace=True)
        data.drop_duplicates(inplace=True)
        return data

    def plot_map_data(self):
        fig = px.scatter_mapbox(self.data, lat="lat", lon="lng", hover_name="vacancy_name",
                                hover_data=["location", "company_name"],
                                color_discrete_sequence=["blue"], zoom=1, height=500, width=1000)
        fig.update_layout(
            mapbox_style="white-bg",
            mapbox_layers=[
                {
                    "below": 'traces',
                    "sourcetype": "raster",
                    "sourceattribution": "Вакансии в России",
                    "source": [
                        "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                    ]
                }
            ])
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

        html_otput = plotly.offline.plot(fig,
                                         config={"displayModeBar": False},
                                         show_link=False,
                                         include_plotlyjs=True,
                                         output_type='div')
        return html_otput
