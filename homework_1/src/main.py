import yaml
import asyncio
import traceback
import warnings
from parsers.objID_parser import get_object_id
from parsers.data_parser import get_data_by_obj_id
from parsers.photo_parser import get_photo_by_obj_id
from data_saver import save_data
warnings.filterwarnings("ignore", category=FutureWarning)


def main():
    CONFIG_PATH = '../config/config.yaml'
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)

    if config['needParsing']['ObjID']:
        print('Получение ID объектов')
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(get_object_id(ids_path=config['path']['objID']))
            print('ID объектов успешно получены\n')
        except Exception:
            print('Ошибка при получении ID объектов\n', traceback.format_exc())

    if config['needParsing']['ObjData']:
        print('Получение данных по объектам')
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(get_data_by_obj_id(ids_path=config['path']['objID'],
                                                       data_path=config['path']['objData']
                                                       )
                                    )
            print('Данные по объектам успешно получены\n')
        except Exception:
            print('Ошибка при получении данных\n', traceback.format_exc())

    if config['savingParams']['needSave']:
        save_data(config=config)
    else:
        print('Сохранение не требуется')

    if config['needParsing']['ObjPhoto']:
        print('Получение фотографий объектов')
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(get_photo_by_obj_id(data_path=config['path']['objData'],
                                                        ids_list=config['getPhotoParams']['objID'],
                                                        photo_path=config['path']['objPhoto']
                                                        )
                                    )
            print('Фото объектов успешно получены\n')
        except Exception:
            print('Ошибка при получении фото объектов\n', traceback.format_exc())


if __name__ == '__main__':
    main()
