#!/usr/bin/env python3
import os
import requests
import xlrd
import pandas as pd
from datetime import date, timedelta
from hargapangan_cleaning import clean_excel
from utils import *

def retrieveData(days, config_path, section):
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
        sqlTableName = '_'.join(filename.lower().split(' '))
        wb = xlrd.open_workbook(file_contents=response.content, ignore_workbook_corruption=True)
        df = pd.read_excel(wb, skiprows=8)
        import_dataframe_to_mysql(config_path, section, df, sqlTableName)

retrieveData(7, 'mysql_config.ini', 'hargapangan_remote')
