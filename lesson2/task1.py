# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем
# должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц
# сайта (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
#   1. Наименование вакансии.
#   2. Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
#   3. Ссылку на саму вакансию.
#   4. Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame
# через pandas. Сохраните в json либо csv.
from bs4 import BeautifulSoup as BS
import requests

from tools.files import save_data_to_json, save_dicts_list_as_csv
from tools.strs import has_numbers, get_number, get_letters


def make_request():
    """
    Запрашивает название должности и количество анализируемых страниц
    Делает запрос
    """
    # Запрашиваем название должности
    prof_name = input('Введите название должности: ')
    # Запрашиваем число анализируемых страниц
    # pages_count = int(input('Введите количество анализируемых страниц: '))

    # Адрес сайта
    url = 'https://hh.ru'
    suffix = '/search/vacancy'
    # Параметры запроса
    # С помощью item_on_page можно задавать количество отображаемых элементов на странице
    params = {'text': prof_name}
    # Заголовок запроса
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

    # Todo добавить задержку между запросами 1 sec, times.sleep(1)
    # Делаем запрос
    return requests.get(url + suffix, params=params, headers=headers)


def parse_response(response):
    """
    Парсит ответ, полученный при запросе на сайт hh.ru
    Собирает список словарей, каждый словарь соответствует одной вакансии и содержит основную информацию о ней
    :param response: ответ на запрос
    :type response: requests.Response
    :rtype: List[Dict]
    """
    dom = BS(response.text, 'html.parser')

    # Список карточек вакансий на сайте
    cards = dom.find_all('div', {'class': 'vacancy-serp-item vacancy-serp-item_redesigned'})
    # Список словарей, каждый словарь содержит информацию об одной вакансии
    jobs = []

    for card in cards:
        # Общий блок карточки вакансии
        tag = card.find('a')
        # Блок с названием компании
        tag_company = card.find('a', {'class': 'bloko-link bloko-link_kind-tertiary'})
        # Блок, в котором находится информация о дате публикации вакансии
        tag_date = card.find('span', {'class': 'bloko-text bloko-text_tertiary'})
        # Блок с информацией о зарплате
        tag_salary = card.find('span', {'class': 'bloko-header-section-3'})
        # Парсим зарплату: минимальное, максимальное значение и валюта
        salary_min, salary_max, salary_curr = get_salary_parsed(tag_salary)

        # Собираем словарь для вакансии
        job_data = {
            'name': tag.text,
            # Todo Надо очищать от спецсимволов названия
            'company': tag_company.text if tag_company else None,
            'location': card.find('div', {'class': 'bloko-text bloko-text_no-top-indent'}).text,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'salary_curr': salary_curr,
            'publish_date': tag_date.text if tag_date else None,
            'link': tag.get('href'),
            'website': 'hh.ru'
        }

        jobs.append(job_data)

    return jobs


def get_salary_parsed(tag):
    """
    Парсит текст тэга, ищет информацию о зарплате и валюте
    :param tag:
    :type tag:
    :return: возвращает кортеж из трех значений (минимальный уровень зарплаты, максимальный уровень зарплаты, валюта)
    :rtype: Tuple(float, float, str)
    """
    if tag is None:
        return [None] * 3

    salary_str = tag.text

    salary_arr = salary_str.split(' ')
    if not salary_arr:
        return [None] * 3

    # Пробуем извлечь валюту из строки
    curr = get_letters(salary_arr[-1])

    numbers = []
    for s in salary_arr:
        if has_numbers(s):
            numbers.append(get_number(s))

    # Если есть 'от', то задано только минимальное значение зарплаты [value, None]
    if 'от' in salary_str:
        numbers.append(None)

    # Если есть 'до', то задано только максимальное значение зарплаты [None, value]
    if 'до' in salary_str:
        numbers.insert(0, None)

    if len(numbers) != 2:
        return None, None, curr

    return *numbers, curr


def main():
    """
    Основная функция
    Делает запрос на сайт hh.ru, получает список вакансий на заданную специальность
    Парсит ответ, собирает все вакансии в виде словаря с единый список
    Сохраняет полученный список в json и csv файл
    """
    # Делаем запрос
    response = make_request()
    # Парсим ответ
    response_parsed = parse_response(response)
    # Сохраняем ответ
    save_dicts_list_as_csv('result.csv', response_parsed)
    save_data_to_json('result.json', response_parsed)


# Вызов основной функции
main()
