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
import time

from tools.files import save_data_to_json, save_dicts_list_as_csv
from tools.strs import has_numbers, get_number, get_letters, convert_to_number, QUIT_SYMBOL
from request_conf import USER_AGENT


def prompt_prof_name():
    """
    Запрашивает у пользователя название профессии, пока будет введена непустая строка
    или не будет введен специальный символ выхода из программы
    :return: название профессии
    :rtype: str
    """
    while True:
        prof_name = input(f'Введите название должности ({QUIT_SYMBOL} для выхода): ')
        # Если был введен символ выхода из цикла, то прекращаем запрос
        if prof_name.lower() == QUIT_SYMBOL:
            return None

        # Если была введена пустая строка, то продолжаем запрашивать
        if not prof_name.split():
            print('Введите непустую строку')
            continue

        return prof_name


def prompt_pages_count():
    """
    Запрашивает у пользователя число анализируемых страниц до тех пор, пока не будет введено корректное значение,
    которое можно сконвертировать в int, или пока не будет введен специальный символ выхода из цикла
    :return: количество анализируемых страниц на hh.ru
    :rtype: int
    """
    while True:
        pages_count_str = input(f'Введите количество анализируемых страниц ({QUIT_SYMBOL} для выхода): ')
        # Если был введен символ выхода из цикла, то прекращаем запрос
        if pages_count_str.lower() == QUIT_SYMBOL:
            return None

        # Пробуем сконвертировать введенную строку в int-число, если было введено некорректное значение, продолжаем
        # запрашивать
        pages_count = convert_to_number(pages_count_str)
        if pages_count is None:
            print('Введите целое число')
            continue

        return pages_count


def make_requests(prof_name, pages_count):
    """
    Делает запрос на сайт hh.ru, получает список вакансий по заданной профессии prof_name, анализирует
    page_count страниц
    :param prof_name: название профессии
    :type prof_name: str
    :param pages_count: количество анализируемых страниц
    :type pages_count: int
    :return: список ответов на запрос по каждой странице
    :rtype: List[requests.Response]
    """
    # Адрес сайта
    url = 'https://hh.ru'
    suffix = '/search/vacancy'

    # Параметры запроса
    # С помощью item_on_page можно задавать количество отображаемых элементов на странице
    params = {'text': prof_name}
    # Заголовок запроса
    headers = {'User-Agent': USER_AGENT}

    # Список ответов, len(responses) = pages_count
    responses = []
    for page in range(pages_count):
        # В словаре с параметрами задаем номер страницы
        params['pages_count'] = page + 1
        # Делаем запрос
        response = requests.get(url + suffix, params=params, headers=headers)

        # Записываем ответ в результирующем списке
        responses.append(response)
        # Делаем задержку между запросами в 1 секунду
        time.sleep(1)

    return responses


def get_responses_parsed(responses):
    """
    Парсит ответы, полученные при запросе на сайт hh.ru
    Каждый ответ соответствует одной странице
    :param responses: список ответов на запрос
    :type responses: List[requests.Response]
    :return: список словарей, каждый словарь соответствует одной вакансии и содержит основную информацию о ней
    :rtype: List[Dict]
    """
    # Общий список словарей с вакансиями из всех страниц
    responses_parsed = []
    for r in responses:
        # Парсим один ответ
        r_parsed = get_response_parsed(r)
        # Объединяем полученный список словарей с общим
        responses_parsed.extend(r_parsed)
    return responses_parsed


def get_response_parsed(response):
    """
    Парсит ответ, полученный при запросе на сайт hh.ru
    Собирает список словарей, каждый словарь соответствует одной вакансии и содержит основную информацию о ней
    :param response: ответ на запрос
    :type response: requests.Response
    :return: список словарей, каждый словарь соответствует одной вакансии и содержит основную информацию о ней
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
        # Блок с локацией
        tag_location = card.find('div', {'class': 'bloko-text bloko-text_no-top-indent'})
        # Парсим зарплату: минимальное, максимальное значение и валюта
        salary_min, salary_max, salary_curr = get_salary_parsed(tag_salary)

        # Собираем словарь для вакансии
        job_data = {
            'name': tag.text,
            'company': tag_company.text if tag_company else None,
            'location': tag_location.text if tag_location else None,
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
    :param tag: тэг, который содержит информацию о зарплате
    :type tag: Tag
    :return: возвращает кортеж из трех значений (минимальный уровень зарплаты, максимальный уровень зарплаты, валюта)
    :rtype: Tuple(float, float, str)
    """
    if tag is None:
        return [None] * 3

    salary_str = tag.text

    salary_arr = [s.lower() for s in salary_str.split(' ')]
    if not salary_arr:
        return [None] * 3

    # Пробуем извлечь валюту из строки
    curr = get_letters(salary_arr[-1])

    numbers = []
    for s in salary_arr:
        if has_numbers(s):
            number = get_number(s)
            if number is not None:
                numbers.append(number)

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
    Запрашивает у пользователя название профессии и количество анализируемых страниц
    Делает запрос на сайт hh.ru, получает список вакансий на заданную профессию
    Парсит ответ, собирает все вакансии в виде списка словарей, где каждый словарь соответствует одной вакансии
    и содержит основную информацию о ней
    Сохраняет полученный список в json и csv файл
    """
    # Запрашиваем у пользователя название профессии для поиска вакансий
    prof_name = prompt_prof_name()
    if prof_name is None:
        return

    # Запрашиваем у пользователя количество анализируемых страниц
    pages_count = prompt_pages_count()
    if pages_count is None:
        return

    # Делаем запросы, один ответ соответствует одной странице
    responses = make_requests(prof_name, pages_count)
    # Парсим ответы в список словарей с вакансиями
    responses_parsed = get_responses_parsed(responses)
    # Сохраняем список словарей с вакансиями
    save_dicts_list_as_csv('result.csv', responses_parsed)
    save_data_to_json('result.json', responses_parsed)


# Вызов основной функции
main()
