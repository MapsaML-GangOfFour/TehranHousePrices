import json
import typing
from itertools import count
from requests import get
from requests.exceptions import RequestException
from time import sleep

WAIT_SECS = 0.5


class ItemsFinished(Exception):
    pass


def pages_getter(total_page: typing.Optional[int] = None, min_price=1, max_price=1000):
    for j in range(min_price, max_price + 1):
        try:
            for i in count(1):
                print(f'بررسی صفحه شماره {i} در رده ی قیمت {j}10,000,000-{j + 1}00,000,000 ')
                link = f'https://api.divar.ir/v8/web-search/tehran/buy-apartment?price={j}10000000-{j + 1}00000000&page={i}'
                requests_error_handler(link, search_page_post_getter)
                if i == total_page:
                    break
        except ItemsFinished:
            pass


def requests_error_handler(link: str, func: typing.Callable) -> typing.Any:
    while True:
        try:
            r = get(link)
            if r:
                return func(r.json())
            else:
                print(f'در خواست با کد {r} برگشته است دوباره پس از {WAIT_SECS} ثانیه امتحان می شود.')
                sleep(WAIT_SECS)
        except RequestException as err:
            print(err)
            print('برای تکرار enter کنید و یا برای بستن برنامه break را تایپ کنید.')
            if input('>') == 'break':
                database_file.close()
                exit()


def search_page_post_getter(data: typing.Dict):
    if data['first_post_date'] == -1:
        raise ItemsFinished
    print(f'\tتعداد {len(data)} مورد در این صفحه یافت شد.')
    for post in data['web_widgets']['post_list']:
        link = f"https://api.divar.ir/v5/posts/{post['data']['token']}"
        print(f'\t{link}...', end='')
        requests_error_handler(link, json_scraper)


def extractor_fun(data, extracted_dict):
    if isinstance(data, list):
        for item in data:
            extractor_fun(item, extracted_dict)
    elif isinstance(data, dict):
        if 'value' in data:
            extracted_dict[data['title']] = data['value']
        for pack in ['items', 'data']:
            if pack in data:
                for item in data[pack]:
                    extractor_fun(item, extracted_dict)


def detail_extractor_fun(data, extracted_dict):
    try:
        for item in data['items']:
            extracted_dict[item['title'].split()[0]] = item['available']
        for item in data['next_page']['widget_list']:
            if 'value' in item['data']:
                extracted_dict[item['data']['title']] = item['data']['value']
            elif 'title' in item['data']:
                extracted_dict.setdefault('امکانات', []).append(item['data']['title'])
        extracted_dict['جزیئات'] = True
        print('کامل شد')
    except KeyError:
        extracted_dict['جزیئات'] = False
        print('قسمت جزیئات نداشت')


def json_scraper(data: typing.Dict):
    list_data = data['widgets']['list_data'][:-1]
    detail_page = data['widgets']['list_data'][-1]
    extracted = {'ناحیه'      : data['data']['district'],
                 'نوع ساختمان': data['data']['category']['title'],
                 'متن توضیحات': data['data']['description'],
                 'token'      : data['data']['webengage']['token']
                 }
    extractor_fun(list_data, extracted)
    detail_extractor_fun(detail_page, extracted)
    database_file.send(extracted)


def json_writer(filename=''):
    item = yield
    full_name = f'database-{filename}.json'
    with open(full_name, 'w') as file:
        file.write('[')
        json.dump(item, file)
    record = 1
    while True:
        try:
            item = yield
            with open(full_name, 'a+') as file:
                file.write(',')
                file.write(json.dumps(item, separators=(',', ':')))
            record += 1
            print(f'رکورد {record} ذخیره شده ')
        except OSError as err:
            print(err)
            if input('برای اتمام برنامه break را تایپ کنید و برای تکرار دوباره اینتر کنید \n>') == 'break':
                raise GeneratorExit
            else:
                pass
        except GeneratorExit:
            with open(full_name, 'a+') as file:
                file.write(']')
                break


if __name__ == '__main__':
    database_file = json_writer('bil1-999')
    database_file.send(None)
    pages_getter(total_page=None, min_price=1, max_price=999)  # تا آخرین صفحه ی دارای اطلاعات پیش می رود
    database_file.close()
