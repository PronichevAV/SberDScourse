import json
import sqlite3
from collections import defaultdict

import numpy as np
import pandas as pd


def is_table_exist(table_name: str, db_path: str = 'src/db/database.db') -> bool:
    """
    Проверка существования таблицы в БД
    """
    db_connection = sqlite3.connect(db_path)
    cursor = db_connection.cursor()
    table_count = len(
        cursor.execute(f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'""").fetchall())
    db_connection.close()
    return table_count != 0


def get_descriptions(db_path: str = 'src/db/database.db') -> np.array:
    """
    Получение текстового описания вакансий из БД
    """
    db_connection = sqlite3.connect(db_path)
    cursor = db_connection.cursor()
    result = cursor.execute("""SELECT tokenized_description FROM data_mart""").fetchall()
    result = np.array(list(map(lambda x: x[0], result)))
    db_connection.close()
    return result


def write_clear_data_to_db(data: pd.DataFrame, table: str, db_path: str = 'src/db/database.db'):
    """
    Запись очищенных данных в витрину (data mart)
    """
    db_connection = sqlite3.connect(db_path)
    data.to_sql(name=table, con=db_connection, if_exists='replace', index=False)
    db_connection.close()


def get_clear_data_from_db(db_path: str = 'src/db/database.db') -> pd.DataFrame:
    """
    Получение очищенных данных из витрины (data mart)
    """
    db_connection = sqlite3.connect(db_path)
    cursor = db_connection.cursor()
    sql_query = """SELECT vacancy_name, company_name, description,
                          vacancy_url, vacancy_id, lat, lng, location
                   FROM data_mart """
    result = cursor.execute(sql_query).fetchall()
    structured_data = defaultdict(list)
    for row in result:
        structured_data['vacancy_name'].append(row[0])
        structured_data['company_name'].append(row[1])
        structured_data['description'].append(row[2])
        structured_data['vacancy_url'].append(row[3])
        structured_data['vacancy_id'].append(row[4])
        structured_data['lat'].append(float(row[5]))
        structured_data['lng'].append(float(row[6]))
        structured_data['location'].append(row[7])
    db_connection.close()
    return pd.DataFrame(structured_data)


def write_raw_data_to_db(items: list, db_path: str = 'src/db/database.db'):
    """
    Запись сырых данных в озеро (data lake)
    """
    data = pd.DataFrame({'data': list(map(lambda x: json.dumps(x), items))})
    db_connection = sqlite3.connect(db_path)
    data.to_sql('data_lake', con=db_connection, if_exists='replace', index=False)
    db_connection.close()


def get_raw_data_from_db(db_path: str = 'src/db/database.db') -> list:
    """
    Получение сырых данных из озера (data lake)
    """
    db_connection = sqlite3.connect(db_path)
    cursor = db_connection.cursor()
    items_str = cursor.execute("""SELECT * FROM data_lake""").fetchall()
    items = list(map(lambda x: json.loads(x[0]), items_str))
    db_connection.close()
    return items
