import re


def has_numbers(s):
    """
    Возвращает флаг, есть ли числа в заданной строке s
    :param s: анализируемая строка
    :type s: str
    :rtype: bool
    """
    return bool(re.search(r'\d', s))


def get_letters(s):
    """
    Возвращает буквы из заданной строки s
    :param s: анализируемая строка
    :type s: str
    :rtype: str
    """
    letters = re.findall("[a-яА-яa-zA-Z]+", s)
    try:
        return letters[0].upper()
    except Exception as e:
        print(f'Не удалось извлечь буквы из строки {s}: {e}')
        return None


def get_number(s):
    """
    Возвращает число, извлеченное из заданной строки s
    Число конвертируется во float
    :param s: анализируемая строка
    :type s: str
    :rtype: float
    """
    number_str = re.sub('[^a-zA-Z0-9 \n\.]', '', s)
    try:
        return float(number_str)
    except Exception as e:
        print(f'Не удалось извлечь числа из строки {s}: {e}')
        return None
