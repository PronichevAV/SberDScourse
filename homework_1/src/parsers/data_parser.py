import asyncio
import concurrent.futures
import joblib
import requests
import pandas as pd
import os


def parse_data(res):
    try:
        object_data = res.json()
        data = object_data['data']
        return data
    except Exception:
        pass
        # print('Ошибка на этапе обработки ответа\nПереход к следующей итерации')


async def get_data_by_obj_id(ids_path='../tmp/ids.pkl', data_path='../tmp/data.pkl'):
    if not os.path.exists(ids_path):
        raise Exception('Отсутствует файл списка ID объектов')

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        ids_list: list = joblib.load(ids_path)
        url = 'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/api/object/'
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(executor, requests.get, f'{url}{id}') for id in ids_list]
        data_list = []
        for response in await asyncio.gather(*futures):
            data_list.append(parse_data(response))
        data = pd.json_normalize(data_list, max_level=10)
        joblib.dump(data, data_path)
