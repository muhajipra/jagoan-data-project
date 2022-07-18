#!/usr/bin/env python3
import os
import requests
import xlrd
import pandas as pd
from datetime import date, timedelta
from hargapangan_cleaning import clean_excel
from utils import *

def retrieveData(days, to_local=False, saved_file_path=None, to_sql=False, config_path=None, section=None):
    market_list = [
        {
            "name": "Pasar Banyuwangi",
            "pid": 16,
            "rid": 49,
            "mid": 170
        },
        {
            "name": "Pasar Rogojampi",
            "pid": 16,
            "rid": 49,
            "mid": 171
        }
    ]

    end_date = date.today()
    start_date = (end_date - timedelta(days=days)).strftime("%d-%m-%Y")
    end_date = end_date.strftime("%d-%m-%Y")
    
    for market in market_list:
        data = {
            'format': 'xls',
            'price_type_id': 1,
            # 'filter_commodity_ids[]': 0,
            'filter_province_ids[]': market["pid"],
            'filter_regency_ids[]': market["rid"],
            'filter_market_ids[]': market['mid'],
            'filter_layout': 'default',
            'filter_start_date': start_date,
            'filter_end_date': end_date,
        }

        filename = market["name"]

        response = requests.post('https://hargapangan.id/tabel-harga/pasar-tradisional/daerah', data=data)
        tableName = '_'.join(filename.lower().split(' '))
        wb = xlrd.open_workbook(file_contents=response.content, ignore_workbook_corruption=True)
        df = pd.read_excel(wb, skiprows=8)
        print(f'{filename} data loaded')

        if to_sql == True:
            import_dataframe_to_mysql(config_path, section, df, tableName)
            print(f'Successfully uploaded {filename} data to MySQL server')
        if to_local == True:
            df.to_excel(os.path.join(saved_file_path, '{}.xlsx'.format(tableName)), index=False)

if __name__ == "__main__":
    range_of_days = int(input('Input the range of days you want to scrape\n'))

    to_sql = repeat_input('Do you want to save the data to MySQL server? (y/n)\n')
    if to_sql == True:
        config_path = input('Input the path of mySQL server configuration\n')
        section = input('Which section of the config to use?\n')
    else:
        config_path = None
        section = None

    to_local = repeat_input('Do you want to save the data to local? (y/n)\n')
    if to_local == True:
        saved_file_path = input('Where do you want to store the data?\n')
    else:
        saved_file_path = None

    retrieveData(days=range_of_days, 
                to_local=to_local,
                saved_file_path=saved_file_path,
                to_sql=to_sql,
                config_path=config_path,
                section=section
                )
    
    
