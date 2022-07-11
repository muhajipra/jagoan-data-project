from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs

import time
from utils import write_json, read_json

def run_browser():
    '''To start the browser'''
    global driver
    global wait
    global action
    #chrome_options = Options()
    #chrome_options.binary_location = "C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
    #chrome_options.headless = True
    driver =  webdriver.Chrome('chromedriver.exe')
    action = ActionChains(driver)
    wait = WebDriverWait(driver, 10)
    driver.get('https://tokopedia.com')

def search(keyword):
    '''Given a keyword, after the browser started will automate searching product from the given keyword'''
# manipulasi link
    global key_string
    key_string = keyword
    key_list = key_string.split(" ")
    key_string = "%20".join(key_list)

    # Wait then find search bar
    try: 
        search_bar = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".e110g5pc0"))) #.css-ubsgp5
        search_bar.send_keys(keyword)

    #find submit button
        search_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".css-1czin5k")))
        search_button.click()
    except:
        print("time out. Koneksi Internetmu mungkin lambat. Error: searchbar/search button")
        driver.quit()

def load_boxInfo():
    '''Waiting for the box info to appear before continuing'''
#Wait box info. Box info contains name product, price product etc.
    try:
        box_info = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-1f2quy8")))#class box info2 produk
    except:
        print("time out. Koneksi Internetmu mungkin lambat.")
        driver.quit()

def scroll_down():
    '''Scrolling down until the end of the page'''
# scroll down to load all boxInfos
    #for down in range(0, steps):
    #    action.send_keys(Keys.PAGE_DOWN).perform()
    #    time.sleep(1.3)

    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    last_page_object = True
    while last_page_object == True:
        action.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1.3)
        last_page = driver.find_elements(By.CLASS_NAME, "css-1ix4b60-unf-pagination-item")
        if len(last_page) > 0:
            last_page_object = False

def get_last_page(soup):
    '''Get the last page number for url generator'''
    #soup = bs(source, 'lxml')
    last_page = int(soup.find_all('button', {'class': 'css-1ix4b60-unf-pagination-item'})[-1].get_text().replace('.', ''))
    return last_page

def page_url_generator(url, splitter, last_page):
    '''Function to generate url for all pages of a product in Tokopedia'''
    page_links = []
    first, third = url.split(splitter)
    navigation, page_num = splitter.split('=')
    for i in range(1, last_page+1):
        new_url = f'{first}{navigation}={i}{third}'
        page_links.append(new_url)
    write_json(page_links, 'tokopedia_page_links.json')
    return page_links

def get_links(soup, destination_list):
    '''Function to scrape all product url given a page'''
    product_urls = soup.select('.css-1f2quy8 > a')
    for product_url in product_urls:
        url = product_url.get('href')
        destination_list.append(url)

def tokopedia_product_url_crawler(url, destination_list):
    driver.get(url)
    load_boxInfo()
    scroll_down()
    soup = bs(driver.page_source, 'lxml')
    get_links(soup, destination_list)

def get_page_urls(last_page):
    driver.find_elements(By.CLASS_NAME, 'css-1eamy6l-unf-pagination-item')[-1].click()
    second_page_url = driver.current_url
    page_urls = page_url_generator(second_page_url, 'page=2', last_page)
    write_json(page_urls, 'tokopedia_page_links.json')
    return page_urls

def multi_page_crawler(keyword):
    product_info = {
        'product_links': []
    }

    run_browser()
    search(keyword)
    load_boxInfo()
    scroll_down()
    soup = bs(driver.page_source, 'lxml')
    last_page = get_last_page(soup)
    navigation_urls = get_page_urls(last_page)
    for i, page_url in enumerate(navigation_urls):
        if i == 50:
            break
        tokopedia_product_url_crawler(page_url, product_info['product_links'])
        write_json(product_info, 'tokopedia_product_links.json')

def single_product_page_scraper(page, info_list):
    soup = bs(page, 'lxml')
    title = soup.find_all('h1', {'class': 'css-1320e6c'})[0].get_text()
    info = soup.find_all('div', {'class': 'items'})[0].get_text()
    price = soup.find_all('div', {'class':'price'})[0].get_text()
    category = soup.select('li[class=css-1dmo88g] > a > b')[0].get_text()
    try:
        shop_credibility = soup.find_all('img', {'class': 'css-ebxddb'})[0].get('alt')
    except:
        shop_credibility = 'NaN'
    shop_name = soup.select('a[class=css-2c1i7f] > h2')[0].get_text()
    sender_place = soup.select('div > div > b')[0].get_text()
    productInfo = {
        'judul': title,
        'info': info,
        'harga': price,
        'kategori': category,
        'status_toko': shop_credibility,
        'nama_toko': shop_name,
        'asal_toko': sender_place
    }
    print(productInfo)
    info_list.append(productInfo)

def product_info_scraper(url_json):
    product_info = {
        'product info': []
    }
    product_urls = read_json(url_json)
    run_browser()
    for i, url in enumerate(product_urls['product_links']):
        if 'ta.tokopedia.com/promo' in url:
            continue

        try:
            driver.get(url)
            info = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-1yuhvjn")))
            page = driver.page_source
            single_product_page_scraper(page, product_info['product info'])
        except:
            print('Cannot scrape')
            print(url)
        if i % 5 == 0:
            write_json(product_info, 'tokopedia_scraped_data.json')

multi_page_crawler('anyaman')
product_info_scraper('tokopedia_product_links.json')
    