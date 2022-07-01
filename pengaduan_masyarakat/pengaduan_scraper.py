import requests
from bs4 import BeautifulSoup as bs
import datetime
import re

def url_crawler(number):
    BASE_URL = 'https://pengaduan.banyuwangikab.go.id/publik/online/web_list'
    data = {
    'page': '{}'.format(number),
    }
    return BASE_URL, data

def get_page(url, data):
    response = requests.post(url, data=data)
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
    skpd = skpd.replace('Skpd tujuan :\n', '').replace('&nbsp', '')
    responder, response_date, response_content = get_response(box)

    if ' ' in time:
        time, hour = time.split(' ')
    if ', ' in skpd:
        skpd = skpd.split(', ')

    complaint = box.select('.expander > p')[0].get_text().replace('\n', ' ')

    return username, time, skpd, complaint, responder, response_date, response_content

def get_content_box(url, data, data_list):
    soup = get_page(url, data)
    content_box = soup.find_all('div', {'class': 'box box-widget'})
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
        data_list.append(complaint_data)
    return data_list


available = True
page_number = 1
report_data = {
    'report': []
}
while available == True:
    base_url, data = url_crawler(page_number)
    test = get_page(base_url, data)
    if not test.find_all('span', {'class': 'username'}):
        available = False
    get_content_box(base_url, data, report_data['report'])
    
    print('Page {} scraped'.format(page_number))
    print(report_data['report'][-1], '\n')
    page_number += 1

print(len(report_data['report']))
