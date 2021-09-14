import json
import typing
from itertools import count
from requests import get
from requests.exceptions import RequestException
from time import sleep

WAIT_SECS = 0.5


def pages_getter(total_page: typing.Optional[int] = None, districts: typing.Optional[typing.List[str]] = None):
    if districts is None:
        districts = ['']
    for district in districts:
        for i in count(1):
            print(f'بررسی صفحه شماره {i} در {district}')
            link = f'https://api.divar.ir/v8/web-search/tehran/buy-apartment?q={district}&price=2000000-&page={i}'
            requests_error_handler(link, search_page_post_getter)
            if i == total_page:
                break


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
                 'متن توضیحات': data['data']['description']
                 }
    extractor_fun(list_data, extracted)
    detail_extractor_fun(detail_page, extracted)
    database_file.send(extracted)


def json_writer():
    item = yield
    with open('database.json', 'w') as file:
        file.write('[')
        json.dump(item, file)
    while True:
        try:
            item = yield
            with open('database.json', 'a+') as file:
                file.write(',')
                file.write(json.dumps(item, separators=(',', ':')))
        except GeneratorExit:
            with open('database.json', 'a+') as file:
                file.write(']')
            break


if __name__ == '__main__':
    Tehran_districts = [line.strip() for line in open('./district.csv', encoding='utf-8')]
    database_file = json_writer()
    database_file.send(None)
    pages_getter(total_page=1, districts=Tehran_districts)  # برای استخراج بی نهایت مقدار ندهید
    database_file.close()
