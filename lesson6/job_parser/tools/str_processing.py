import re


def convert_to_number(var_str, func=int, undef_value=None):
    """
    Конвертация строки в число такого типа, определяемого функцией приведения func
    Если не сможет сконвертировать, вернет None
    :param var_str: значение, которое будет сконвертировано
    :type var_str: str
    :param func: функция приведения
    :type func: function
    :param undef_value: выходное значение, если не удалось сконвертировать
    :return: число
    :type: тип func
    """
    # Функция преобразования может быть не определена, в этом случае возвращается None
    if func is None:
        return undef_value

    # Иначе пробуем сконвертировать в тип func
    try:
        return func(var_str)
    except ValueError as e:
        # print(f'Не удалось сконвертировать в число: {e}\n')
        return undef_value


def get_number(s):
    """
    Возвращает число, извлеченное из заданной строки s
    Число конвертируется в int
    :param s: анализируемая строка
    :type s: str
    :rtype: int
    """
    # Все символы, которые не числа заменяет на пустую строку
    number_str = re.sub('[^0-9]', '', s)
    # Пробуем сконвертировать в int
    return convert_to_number(number_str)


def get_letters(s):
    """
    Возвращает буквы из заданной строки s
    :param s: анализируемая строка
    :type s: str
    :rtype: str
    """
    letters = re.findall('[a-яА-яa-zA-Z]+', s)
    if letters:
        return letters[0]
