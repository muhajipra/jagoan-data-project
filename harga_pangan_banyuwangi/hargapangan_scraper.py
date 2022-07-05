#!/usr/bin/env python3
import os
import requests
import xlrd
import pandas as pd
from datetime import date, timedelta
from hargapangan_cleaning import clean_excel

def retrieveData(days):
    market_list = [
        {
            "name": "Pasar Banyuwangi",
            "pid": 16,
            "rid": 49,
            "mid": 170
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
        with open(filename + '.xls', 'wb') as f:
            f.write(response.content)

        # Process Files and Convert to CSV
        wb = xlrd.open_workbook(filename + '.xls', ignore_workbook_corruption=True)
        df = pd.read_excel(wb, skiprows=8)
        df = df.replace(r'\n', '', regex=True)
        df = df.drop(columns=['No.'])
        os.remove(filename + '.xls')
        df.to_excel(filename + '.xlsx', index=False)
        clean_excel(filename)
        

retrieveData(30)
