import json
import random
import time

from bs4 import BeautifulSoup
import requests
from fake_headers import Headers

headers = Headers(headers=True).generate()


def get_html(url):
    response = requests.get(url, headers=headers)
    return response.text


def get_categories():
    with open('main.html', encoding='utf-8') as f:
        source = f.read()
    soup = BeautifulSoup(source, 'lxml')

    categories = soup.find('ul', class_="ni").find_all('a')
    categories_links = []
    for category in categories:
        categories_links.append('https://www.eldorado.ru' + category.get('href'))
    return categories_links


def get_subcategory(category_url):
    source = get_html(category_url)
    soup = BeautifulSoup(source, 'lxml')
    subcategories = soup.find('div', class_='Po').find_all('div', class_="cp")
    subcategories_links = []
    for subcategory in subcategories:
        subcategories_links.append('https://www.eldorado.ru' + subcategory.find('a').get('href'))
    return subcategories_links


def get_subsubcategory(subcategories_url):
    source = get_html(subcategories_url)
    soup = BeautifulSoup(source, 'lxml')
    subsubcategories = soup.find('div', class_='Qo').find_all('a')
    subsubcategories_links = []
    for subsubcategory in subsubcategories:
        subsubcategories_links.append('https://www.eldorado.ru' + subsubcategory.get('href'))
    return subsubcategories_links


def get_products(subsubcategories_url):
    source = get_html(subsubcategories_url)
    soup = BeautifulSoup(source, 'lxml')
    products = soup.find('div', id="listing-container").find('ul').find_all('li', class_="eE")
    products_links = []
    for product in products:
        link = product.find('a', class_="lE").get('href')
        products_links.append('https://www.eldorado.ru' + link)
    return products_links


def find_reviews(source):
    data = list()
    soup = BeautifulSoup(source, 'lxml')
    reviews = soup.find_all('div', class_="usersReviewsListItem")
    if len(reviews) == 0:
        return data
    for review in reviews:
        user_name = review.find('span', class_="userName").text.strip()
        print(user_name)
        user_from = review.find('span', class_="userFrom").text.strip()
        print(user_from)
        review_date = review.find('div', class_="userReviewDate").text.strip()
        print(review_date)
        helpfulness_review = review.find('div', class_="middleBlockItem").find('b').text.strip()
        print(helpfulness_review)
        review_text = review.find('div', class_="middleBlockItem").text.strip()
        review_text = review_text.replace(helpfulness_review, '').replace('\n', '').replace('\r', '').strip()
        print(review_text)
        rate = len(review.find('div', class_="itemRate").find_all('div', class_="starFull"))
        print(rate)
        data.append(
            {
                'author': user_name,
                'from': user_from,
                'date': review_date,
                'stars': rate,
                'text': review_text,
                'helpfulness': helpfulness_review
            }
        )
    return data


def get_reviews(product_url):
    data = {
        'url': product_url,
        'reviews': []
    }
    source = get_html(product_url + '?show=response')
    soup = BeautifulSoup(source, 'lxml')
    pages = soup.find('div', class_="pages")
    if pages is not None:
        page_links = pages.find_all('a')
        if len(page_links) == 0:
            page_count = 1
        else:
            page_count = int(page_links[-1].text)
    else:
        page_count = 1
    for page_num in range(1, page_count + 1):
        source = get_html(product_url + f'page/{page_num}/?show=response')
        reviews = find_reviews(source)
        if reviews is not None:
            for review in reviews:
                data['reviews'].append(review)
            time.sleep(random.uniform(2, 10))
    return data


if __name__ == '__main__':
    categories = get_categories()
    for category in categories[:3]:
        subcategory = get_subcategory(category)[0]
        subsubcategory = get_subsubcategory(subcategory)[0]
        products = get_products(subsubcategory)
        for num, product in enumerate(products[:3]):
            r = get_reviews(product)
            with open(f'reviews files/review{num}.json', 'w', encoding='utf-8') as file:
                json.dump(r, file, ensure_ascii=False, indent=4)
            time.sleep(random.uniform(2, 10))
