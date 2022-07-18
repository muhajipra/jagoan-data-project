import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import csv
import datetime
import json
import re
from utils import read_json, write_json

def label_duplicate(row):
    if len(row['SKPD Tujuan']) > 1:
        val = True
    return val

def write_excel(data, title):
    csv_file = '{}.csv'.format(title)
    dict_keys = data[0].keys()
    with open(csv_file, 'w', encoding="utf-8") as f:
        w = csv.DictWriter(f, dict_keys)
        w.writeheader()
        w.writerows(data)
    
    excel_file = '{}.xlsx'.format(title)
    df = pd.read_csv(csv_file)
    df['SKPD Tujuan'] = df['SKPD Tujuan'].apply(eval)
    df['Duplicated'] = df['SKPD Tujuan'].str.len() > 1
    df = df.explode('SKPD Tujuan')
    df.to_excel(excel_file, index=False)

def url_crawler(base_url, number):
    data = {
    'page': '{}'.format(number),
    }
    return base_url, data

def get_page(url, data, headers):
    response = requests.post(url, data=data, headers=headers)
    soup = bs(response.text, features='lxml')
    return soup

def get_response(box):
    try:
        response = box.find_all('a', {'class': 'btn btn-success btn-xs pull-right'})[0].get('onclick')
        response_id = re.findall('[0-9]+', response)[0]
        response = requests.get('https://pengaduan.banyuwangikab.go.id/publik/tanggapan/{}'.format(response_id))

        soup = bs(response.text, features='lxml')
        responder_institution = soup.find_all('span', {'class': 'direct-chat-name'})[0].get_text()
        response_date = soup.find_all('span', {'class': 'direct-chat-timestamp pull-left'})[0].get_text()
        response_content = soup.find_all('div', {'class': 'direct-chat-text'})[0].get_text().replace('\n', '')
    except:
        responder_institution, response_date, response_content = None, None, None
    return responder_institution, response_date, response_content

def get_data(box):
    username = box.find_all('span', {'class': 'username'})[0].get_text()
    time, skpd = box.find_all('span', {'class': 'description'})[0].get_text().split(' | ')
    skpd = skpd.replace('Skpd tujuan :\n', '').strip()
    responder, response_date, response_content = get_response(box)

    if ' ' in time:
        time, hour = time.split(' ')
    if '&nbsp' in skpd:
        skpd = skpd.split('&nbsp')
        skpd = list(set(skpd))
        if '' in skpd:
            skpd.remove('')

    complaint = box.select('.expander > p')[0].get_text().replace('\n', ' ')

    return username, time, skpd, complaint, responder, response_date, response_content

def get_content_box(url, data, headers, data_list):
    soup = get_page(url, data, headers)
    content_box = soup.find_all('div', {'class': 'box box-widget'})
    source = url.split('/')[-1]
    for content in content_box:
        username, time, skpd, complaint, responder, response_date, response_content = get_data(content)
        complaint_data = {
            'Sumber': source,
            'Nama': username,
            'Waktu Laporan': time,
            'SKPD Tujuan': skpd,
            'Keluhan': complaint,
            'Balasan dari Dinas Terkait': responder,
            'Tanggal Balasan': response_date,
            'Balasan': response_content
        }
        data_list.append(complaint_data)

def make_pengaduan_dataset(base_urls, headers, start, end=0):
    report_data = []
    for base_url in base_urls:
        available = True
        page_number = start
        while available == True:
            if end != 0:
                if page_number == end:
                    available = False
            
            base_url, data = url_crawler(base_url, page_number)
            source = base_url.split('/')[-1]
            test = get_page(base_url, data, headers)
            if not test.find_all('span', {'class': 'username'}):
                available = False
            get_content_box(base_url, data, headers, report_data)

            print(f'Page {page_number} in {source} scraped')
            if page_number % 50 == 0:
                write_json(report_data, 'backup_pengaduan.json')
            page_number += 1

    write_excel(report_data, 'pengaduan_masyarakat')

headers = {
    'authority': 'pengaduan.banyuwangikab.go.id',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,id;q=0.8',
    # 'content-length': '0',
    # 'cookie': 'ci_session=55b627720a6d69687d9aefe1940a02ceeacce066',
    'origin': 'https://pengaduan.banyuwangikab.go.id',
    'referer': 'https://pengaduan.banyuwangikab.go.id/publik/sms',
    'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49',
    'x-requested-with': 'XMLHttpRequest',
}

base_urls = ['https://pengaduan.banyuwangikab.go.id/publik/online/web_list']
make_pengaduan_dataset(base_urls, headers, 1)
