import asyncio
import concurrent.futures
import multiprocessing
import os

import pandas as pd
import requests
from joblib import Parallel, delayed, load


async def get_photo_by_obj_id(data_path='../tmp/data.pkl', ids_list=None, photo_path='../data/photo/'):
    if ids_list is None:
        print('Список идентификаторов не задан.\nПолучение демонстрационного изображения.')
        ids_list = [38368]
    if not os.path.exists(data_path):
        raise Exception('Отсутствует файл списка ID объектов')

    data: pd.DataFrame = load(data_path)[['id', 'miniUrl']]
    df_filter = data['id'].isin(ids_list)
    data = data[df_filter]
    obj_ids, urls = list(data['id']), list(data['miniUrl'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(executor, requests.get, url) for url in urls]
        responses = []
        for response in await asyncio.gather(*futures):
            responses.append(response)

    num_cores = multiprocessing.cpu_count()
    _ = Parallel(n_jobs=num_cores, verbose=0)(
        delayed(save_photo)(obj_id, res, photo_path) for obj_id, res in zip(obj_ids, responses))


def save_photo(obj_id, response, photo_path):
    with open(photo_path + str(obj_id) + '.jpg', 'wb') as img:
        img.write(response.content)
