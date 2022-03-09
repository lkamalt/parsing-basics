# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой
# суммы (необходимо анализировать оба поля зарплаты). Для тех, кто выполнил задание с Росконтролем - напишите запрос
# для поиска продуктов с рейтингом не ниже введенного или качеством не ниже введенного (то есть цифра вводится одна,
# а запрос проверяет оба поля)
import pymongo
from pprint import pprint

from config.mongo_conf import HOST, PORT
from tools.strs import QUIT_SYMBOL, convert_to_number
from tools.common import clear_dict_from_nbsp


def prompt_salary():
    """
    Запрашивает у пользователя значение зарплаты до тех пор, пока не будет введено корректное значение,
    которое можно сконвертировать в int, или пока не будет введен специальный символ выхода из цикла
    :return: значение зарплаты
    :rtype: int
    """
    while True:
        # Введенное число, тип str
        salary_str = input(f'Введите значение заработной платы ({QUIT_SYMBOL} для выхода): ')
        if salary_str.lower() == QUIT_SYMBOL:
            return None

        salary = convert_to_number(salary_str)
        if salary is None:
            print('Введите целое число')
            continue

        return salary


def show_jobs_with_greater_salary(salary):
    """
    Выводит список вакансий базы данных со значением зарплаты выше заданного значения salary
    :param salary: сравниваемое значение зарплаты, введенное пользователем
    :type salary: int
    """
    with pymongo.MongoClient(HOST, port=PORT) as client:
        # База данных
        db_jobs = client.db_jobs
        # Коллекция
        jobs = db_jobs.jobs

        print(f'Список вакансий с зарплатой > {salary}:')
        for job in jobs.find({}):
            salary_min = job['salary_min']
            salary_max = job['salary_max']
            if (salary_min is not None and salary_min > salary) or (salary_max is not None and salary < salary_max):
                # Очищаем строковые значения словаря от символа неразрывного пробела
                clear_dict_from_nbsp(job)
                # Выводим словарь в консоль
                pprint(job)


def main():
    """
    Основная функция
    Запрашивает значение зарплаты (целое число) у пользователя в консоли
    Выводит вакансии из БД с зарплатой, которая больше введенного числа
    """
    # Запрашиваем у пользователя значение зарплаты
    salary = prompt_salary()
    if salary is None:
        return

    # Выводит вакансии с большей зарплатой
    show_jobs_with_greater_salary(salary)


# Вызов основной функции
main()
