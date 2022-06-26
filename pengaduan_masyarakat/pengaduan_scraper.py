import requests
from bs4 import BeautifulSoup as bs
import datetime
import re

BASE_URL = 'https://pengaduan.banyuwangikab.go.id/publik/online/web_list'
data = {
    'page': '4',
}

def get_page(url, data):
    response = requests.post(url, data=data)
    soup = bs(response.text, features='lxml')
    return soup

def get_response(box):
    response = box.find_all('a', {'class': 'btn btn-success btn-xs pull-right'})[0].get('onclick')
    response_id = re.findall('[0-9]+', response)[0]
    response = requests.get('https://pengaduan.banyuwangikab.go.id/publik/tanggapan/{}'.format(response_id))

    soup = bs(response.text, features='lxml')
    responder_institution = soup.find_all('span', {'class': 'direct-chat-name'})[0].get_text()
    response_date = soup.find_all('span', {'class': 'direct-chat-timestamp pull-left'})[0].get_text()
    response_content = soup.find_all('div', {'class': 'direct-chat-text'})[0].get_text().replace('\n', '')
    return responder_institution, response_date, response_content

def get_data(box):
    username = box.find_all('span', {'class': 'username'})[0].get_text()
    time, skpd = box.find_all('span', {'class': 'description'})[0].get_text().split(' | ')
    skpd = skpd.replace('Skpd tujuan :\n', '').replace('&nbsp', '')
    responder, response_date, response_content = get_response(box)

    #if ' ' in time:
    #    date, time = time.split(' ')
    if ', ' in skpd:
        skpd = skpd.split(', ')

    complaint = box.select('.expander > p')[0].get_text().replace('\n', ' ')

    return username, time, skpd, complaint, responder, response_date, response_content

def get_content_box(url, data):
    soup = get_page(url, data)
    content_box = soup.find_all('div', {'class': 'box box-widget'})
    data = []
    for content in content_box:
        username, time, skpd, complaint, responder, response_date, response_content = get_data(content)
        complaint_data = {
            'Nama': username,
            'Waktu Laporan': time,
            'SKPD Tujuan': skpd,
            'Keluhan': complaint,
            'Balasan dari Dinas Terkait': responder,
            'Tanggal Balasan': response_date,
            'Balasan': response_content
        }
        data.append(complaint_data)
    return data
        

data_keluhan = get_content_box(BASE_URL, data)
for data in data_keluhan:
    for key in data.keys():
        print('{}: {}'.format(key, data[key]))
    print('\n')
#print(get_page(BASE_URL, data))