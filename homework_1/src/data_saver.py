import pandas as pd
import os
import joblib
import traceback
import sqlite3


def create_connection(db_path):
    return sqlite3.connect(db_path)


def save_data(config):
    if os.path.exists(config['path']['objData']):
        data: pd.DataFrame = joblib.load(config['path']['objData'])
        connection = None

        if config['savingParams']['ToPkl']:
            try:
                data.to_pickle(config['savingParams']['dataPath'] + '.pkl')
                print('Данные успешно сохранены в формате Pickle')
            except Exception:
                print('Ошибка при сохранении данных в формат Pickle\n', traceback.format_exc())

        if config['savingParams']['ToCsv']:
            try:
                data.to_csv(config['savingParams']['dataPath'] + '.csv')
                print('Данные успешно сохранены в формате CSV')
            except Exception:
                print('Ошибка при сохранении данных в формат CSV\n', traceback.format_exc())

        if config['savingParams']['ToExcel']:
            try:
                data = data.applymap(str)
                for column in data.columns:
                    data[column] = data[column].apply(lambda x: x[:32765])
                data.to_excel(config['savingParams']['dataPath'] + '.xls')
                print('Данные успешно сохранены в формате Excel')
            except Exception:
                print('Ошибка при сохранении данных в формат Excel\n', traceback.format_exc())

        if config['savingParams']['ToDB']:
            try:
                connection = create_connection(db_path=config['DBParams']['DBPath'])
                print('Успешное подключение к БД')
            except Exception:
                print('Не удалось подключиться к БД\n', traceback.format_exc())

        if connection:
            try:
                data.applymap(str).to_sql(name=config['DBParams']['tableName'],
                                          con=connection,
                                          if_exists='replace'
                                          )
                print('Данные успешно сохранены в БД')
                connection.close()
                print("Соединение с БД закрыто")
            except Exception:
                print('Ошибка при сохранении данных в БД>\n', traceback.format_exc())
    else:
        print('Данные для сохранения отсутствуют')