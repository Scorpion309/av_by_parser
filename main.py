from bs4 import BeautifulSoup
import requests
import csv
from _datetime import datetime

def time_for_func(func):

    def wrapper():
        start = datetime.now()
        func()
        stop = datetime.now()
        print('На парсинг сайта затрачено:', str(stop-start), ' секунд')
    return wrapper


def get_html(url):
    return requests.get(url).text

def get_data(html, cars):
    soup = BeautifulSoup(html, 'lxml')
    # get table with cars
    info = soup.find('div', class_="listing__items")
    # get info for car
    info = info.find_all('div', class_="listing-item")

    for inf in info:
        l = inf.find('a', class_="listing-item__link").get('href')
        link = 'https://cars.av.by' + l
        l = l.split('/')
        # get price
        try:
            price = inf.find('div', class_="listing-item__priceusd").text.replace(u'\xa0', u' ').replace(u'\u2009', u'').strip('≈ ').strip(' $')
        except:
            price = 'No price'

        # get params
        try:
            params = inf.find('div', class_="listing-item__params").text.replace(u'\xa0', u' ').replace(u'\u2009', u' ')
            # get year
            try:
                year = params.split()[0]
            except:
                year = 'No information'
            # get gear
            try:
                gear = params.split()[1].strip('г.').strip(', ')
            except:
                gear = 'No information'
            # get engine
            try:
                engine = params.split()[2]
            except:
                engine = 'No information'
            # get fuel
            try:
                fuel = params.split()[4][:6]
            except:
                fuel = 'No information'
        except:
            year = 'No information'
            gear = 'No information'
            engine = 'No information'
            fuel = 'No information'

        # update dict
        cars.update( {l[-1]: {
                            'brand': l[1],
                            'model': l[2],
                            'year': year,
                            'engine': engine,
                            'fuel': fuel,
                            'gear': gear,
                            'price': price,
                            'link': link
                            }
                    })

    return cars

def get_full_data(html, cars, id):
    soup = BeautifulSoup(html, 'lxml')

    # get odometer
    try:
        odometer = soup.find('div', class_="card__params").find('span').text.replace(u'\xa0', u' ').replace(u'\u2009', u'')
    except:
        odometer = 'No information'

    # get text
    try:
        text = soup.find('div', class_="card__comment-text").find('p').text.replace(u'\xa0', u' ').replace(u'\u2009', u'').replace('≈', ' ')
    except:
        text = 'No text'
    # update cars
    cars[id].update({'odometer': odometer, 'text': text})

    return cars

def save_to_scv(data):
    with open('data.csv', 'w') as outfile:
        writer = csv.writer(outfile)
        for i in data:
            try:
                writer.writerow(data[i].values())
            except:
                print(f'Произошла ошибка записи информации об автомобиле с id={i}. Это автомобиль: {data[i]}')


if __name__ == '__main__':
    @time_for_func
    def main():
        cars = {}
        # count pages
        count = int(input("Введите количество страниц сайта для парсинга (каждая по 25 объявлений):"))
        # url
        for page in range(1, count+1):
            print(f'Гружу {page}-ую страницу сайта:')
            url = "https://cars.av.by/filter?price_currency=2&page=" + str(page)
            # get cars
            cars = get_data(get_html(url), cars)
            # get full information for cars
            [get_full_data(get_html(cars[i]['link']), cars, i) for i in cars]

            # print cars
            [print(cars[i]) for i in cars]

        # save to scv file
        save_to_scv(cars)

    main()


