import asyncio
import concurrent.futures
import joblib
import requests
import itertools


def parse_ids(res):
    try:
        object_data = res.json()
        ids = list(map(lambda x: x['objId'], object_data['data']['list']))
        return ids
    except Exception:
        pass
        # print('Ошибка на этапе обработки ответа\nПереход к следующей итерации')


async def get_object_id(ids_path='../tmp/object_ids.pkl'):
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        limit = 1000
        offsets = range(0, 11001, limit)
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(executor, requests.get,
                                        f'https://xn--80az8a.xn--d1aqf.xn--p1ai/сервисы/api/kn/object?offset={offset}&limit={limit}&sortField=objAddr&sortType=desc&objStatus=0')
                   for offset in offsets]
        ids_list = []
        for response in await asyncio.gather(*futures):
            ids_list.append(parse_ids(response))
        ids_list = list(itertools.chain(*[ids for ids in ids_list if ids is not None]))
        joblib.dump(ids_list, ids_path)
