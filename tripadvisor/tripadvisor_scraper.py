import requests
from bs4 import BeautifulSoup as bs
from utils import read_json, write_json
import os
import pandas as pd
import numpy as np

def request_page(url, config_path):
    '''Given a URL, will use requests to get the page html and return beautifulsoup object'''
    web_data = read_json(config_path)
    response = requests.get(url, headers=web_data['headers'], cookies=web_data['cookies'])
    soup = bs(response.text, features='html.parser')
    return soup

def get_rating(soup):
    ''' Given soup object will get the rating box from the first page '''
    rating_box = soup.find_all('div', {'class': 'yFKLG'})[0]    # Getting the rating box that contains all rating and average rating

    # Get the average rating and total reviews
    average_rating = float(soup.find_all('div', {'class': 'biGQs _P fiohW hzzSG uuBRH'})[0].get_text())
    total_reviews = int(soup.find_all('span', {'class': 'biGQs _P pZUbB biKBZ KxBGd'})[0].get_text().replace('.', ''))

    # Get the categories of rating from very good till bad
    rating_label = soup.find_all('div', {'class': 'biGQs _P pZUbB hmDzD'})[:5]
    rating_label = [label.get_text() for label in rating_label]
    rating_number = soup.find_all('div', {'class': 'biGQs _P pZUbB osNWb'}) 
    rating_number = [number.get_text().replace('.', '') for number in rating_number][:5]
    rating_number = [int(number) for number in rating_number]

    # Give the rating as dictionary
    ratings = {
        'average_rating': average_rating,
        'total_reviews': total_reviews,
        'rating_description': []
    }

    for i, label in enumerate(rating_label):
        rating = {label: rating_number[i]}
        ratings['rating_description'].append(rating)

    return ratings

def get_reviews_page(soup):
    ''' Get the container for all reviews in one page '''
    review_container = soup.find_all('div', {'class': 'LbPSX'})[0]
    return review_container

def get_review_boxes(reviews_container):
    review_boxes = reviews_container.find_all('div', {'class': '_c'})
    return review_boxes

def get_review_data(review_box):
    # Get the citizenship of the reviewer
    citizenship_box = review_box.find_all('div', {'class': 'biGQs _P pZUbB osNWb'})
    citizenship = [citizen.find('span').get_text() for citizen in citizenship_box]
    for i, citizen in enumerate(citizenship):
        if 'kontribusi' in citizen:
            citizenship[i] = 'NaN'
    citizenship = citizenship[0]

    # Get the headline
    headline, review = review_box.find_all('span', {'class': 'yCeTE'})
    headline, review = headline.get_text(), review.get_text()

    # Get Status
    try:
        arrival_data = review_box.find_all('div', {'class': 'RpeCd'})[0].get_text()
    except:
        arrival_data = 'NaN'

    # Get rating
    rating_given = review_box.find_all('svg', {'class': 'UctUV d H0'})[0].get('aria-label')

    return citizenship, headline, review, arrival_data, rating_given

def get_data(url, config_path):
    soup = request_page(url, config_path)
    reviews_page = get_reviews_page(soup)
    review_boxes = get_review_boxes(reviews_page)
    data = []
    for review_box in review_boxes:
        citizenship, headline, review, arrival_data, rating_given = get_review_data(review_box)
        information = {
            'asal': citizenship,
            'keterangan': arrival_data,
            'rating': rating_given,
            'judul': headline,
            'ulasan': review
        }
        data.append(information)

    return data

def create_urls(first_url, config_path):
    soup = request_page(first_url, config_path)
    end_page = int(soup.find_all('div', {'class': 'Ci'})[0].get_text().split(' ')[-2])
    splitter = '-Reviews-'
    first_part, third_part = first_url.split(splitter)
    url_list = [first_url]
    for i in range(10, end_page, 10):
        url = '{}{}or{}-{}'.format(first_part, splitter, i, third_part)
        url_list.append(url)

    return url_list

def get_multi_urls(first_url, config_path):
    first_page = request_page(first_url, config_path)
    rating = get_rating(first_page)
    write_json(rating, 'rating.json')

    reviews_data = []
    url_list = create_urls(first_url, config_path)
    exception = []
    for i, url in enumerate(url_list):
        try:
            reviews = get_data(url, config_path)
            print('Page {}/{} successfully scraped'.format(i+1, len(url_list)))
            for review in reviews:
                reviews_data.append(review)
        except:
            print('Page {}/{} failed to scrape'.format(i+1, len(url_list)))
            exception.append(url)

    if exception is not []:
        write_json(exception, 'exempt.json')
    write_json(reviews_data, 'tripadvisor_reviews.json')

    return reviews_data


url = 'https://www.tripadvisor.co.id/Attraction_Review-g317103-d447076-Reviews-Ijen_Crater-Banyuwangi_East_Java_Java.html'
config_path = 'tripadvisor/config.json'

#get_multi_urls(url, config_path)

data = read_json('tripadvisor_reviews.json')

df = pd.DataFrame.from_dict(data)
df.to_excel('tripadvisor_reviews.xlsx')