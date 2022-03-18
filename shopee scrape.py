from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import httpx
from datetime import datetime

driver_path = r"C:\Users\HP\Downloads\chromedriver_win32\chromedriver.exe"

output = pd.DataFrame(columns=['Index','Shop_Name', 'Prod_Name', 'Currency', 'Price', 'Unit_Sold', 'Product_Description',
                               'Average_Rating', 'Buyer_Rating', 'Buyer_Review', 'Review_Time', 'URL'])

url_input = input('Enter target url:')

file_name = input('Enter file name:')
start_time = time.time()

driver = webdriver.Chrome(executable_path=driver_path)

all_urls = []

for page in range(5):

    #     product_list = 'https://shopee.com.my/search?keyword=' + str(keyword) + '&page=' + str(page)
    driver.get(url_input)

    if page == 0:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,
                                                                   '//div[@class="language-selection__list-item"]/button[1]'))).click()
    else:
        WebDriverWait(driver, 5)
    time.sleep(3)

    for x in range(10):
        driver.execute_script("window.scrollBy(0,300)")
        time.sleep(0.1)

    all_items = driver.find_elements_by_xpath('//a[@data-sqe="link"]')

    for item in all_items:
        url = item.get_attribute('href')
        all_urls.append(url)

driver.quit()

index = 0

for url in all_urls:
    ids = url.split('-i.')[1].split('.')
    shop_id = ids[0]
    prod_id = ids[1]

    shop_api = 'https://shopee.com.my/api/v2/shop/get?is_brief=1&shopid=' + str(shop_id)
    shop_name = httpx.get(shop_api).json().get('data')['name']

    item_api = 'https://shopee.com.my/api/v2/item/get?itemid=' + str(prod_id) + '&shopid=' + str(shop_id)
    item_detail = httpx.get(item_api).json().get('item')
    price = item_detail['price_min'] / 100000
    price_before_discount = item_detail['price_min_before_discount']
    prod_brand = item_detail['brand']
    prod_categories = item_detail['categories'][0]['display_name']
    currency = item_detail['currency']
    unit_sold = item_detail['historical_sold']
    prod_name = item_detail['name']
    prod_desc = item_detail['description'].replace('\n', ' ').replace('  ', ' ')
    average_rating = item_detail['item_rating']['rating_star']

    review_api = 'https://shopee.com.my/api/v2/item/get_ratings?filter=0&flag=1&itemid=' + str(
        prod_id) + '&limit=20&offset=0&shopid=' + str(shop_id) + '&type=0'
    review_detail = httpx.get(review_api).json().get('data')['ratings']

    if review_detail == []:
        buyer_rating = 'NA'
        buyer_review = 'NA'
        review_time = 'NA'

        output = output.append([{'Index': index, 'Shop_Name': shop_name, 'Prod_Name': prod_name, 'Currency': currency,
                                 'Price': price, 'Unit_Sold': unit_sold, 'Average_Rating': average_rating,
                                 'Buyer_Rating': buyer_rating, 'Buyer_Review': buyer_review, 'Review_Time': review_time,
                                 'URL': url, 'Category': category}], sort=False)

    else:
        for i in range(len(review_detail)):
            buyer_rating = review_detail[i]['rating_star']
            buyer_review = review_detail[i]['comment']
            review_time = datetime.fromtimestamp(review_detail[i]['ctime']).strftime('%Y-%m-%d %H:%M:%S')

            output = output.append(
                [{'Index': index, 'Shop_Name': shop_name, 'Prod_Name': prod_name, 'Currency': currency,
                  'Price': price, 'Unit_Sold': unit_sold, 'Product_Description': prod_desc,
                  'Average_Rating': average_rating, 'Buyer_Rating': buyer_rating, 'Buyer_Review': buyer_review,
                  'Review_Time': review_time, 'URL': url}], sort=False)

    index += 1

output = output.set_index(['Index'])
output.to_csv('ShopeeScrape_' + str(file_name) + '_' + str(datetime.now().strftime('%Y%m%d_%H%M%S')) + '.csv')

