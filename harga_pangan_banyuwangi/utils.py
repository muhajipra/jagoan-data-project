import json
from configparser import ConfigParser
import sqlalchemy

def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def write_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def read_mysql_config(path, section):
    config = ConfigParser()
    config.read(path)

    username = config.get(section, 'username')
    password = config.get(section, 'password')
    ip = config.get(section, 'ip')
    database_name = config.get(section, 'database_name')

    return username, password, ip, database_name

def import_dataframe_to_mysql(path, section, dataframe, table_name):
    username, password, ip, database_name = read_mysql_config(path, section)

    database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
                                                   format(username, password, 
                                                          ip, database_name))
    dataframe.to_sql(con=database_connection, name=table_name, if_exists='replace')