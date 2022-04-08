# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные
# о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from config.login_data import LOGIN, PASSWORD
from tools.base_parser import BaseParser
from tools.files import save_data_to_json


class MailRuParser(BaseParser):
    """ Класс парсера сайта mail.ru """

    def __init__(self):
        super().__init__()
        self._driver = webdriver.Chrome(executable_path='chromedriver.exe')
        self._wait = WebDriverWait(self._driver, 10)

    @property
    def main_url(self):
        return 'https://account.mail.ru/login/'

    @property
    def db_name(self):
        return 'db_letters'

    @property
    def collection_name(self):
        return 'letters'

    def _get_clickable_elem(self, by, by_name):
        """
        Возвращает кликабельный элемент по заданному расположению
        :param by: по чему производится поиск
        :type by: By
        :param by_name: название расположения
        :type by_name: str
        :rtype: WebElement
        """
        return self._wait.until(EC.element_to_be_clickable((by, by_name)))

    def _get_visible_elem(self, by, by_name):
        """
        Возвращает видимый элемент по заданному расположению
        :param by: по чему производится поиск
        :type by: By
        :param by_name: название расположения
        :type by_name: str
        :rtype: WebElement
        """
        return self._wait.until(EC.visibility_of_element_located((by, by_name)))

    def _get_letters_links(self):
        """
        Собирает список ссылок, каждая из которых соответствует одному письму
        :rtype: List[str]
        """
        # Список ссылок писем, делаем его множеством, чтобы исключить дубли
        links = set()
        try:
            self._driver.get(self.main_url)

            # Снимаем галочку с Запомнить
            chb_save_auth = self._get_clickable_elem(By.CLASS_NAME, 'save-auth-field-wrap')
            chb_save_auth.click()

            # Вводим логин
            txt_login = self._driver.find_element(By.CLASS_NAME, 'input-0-2-77')
            txt_login.send_keys(LOGIN)

            # Нажимаем на кнопку Ввести пароль
            btn_submit = self._driver.find_element(By.CLASS_NAME, 'submit-button-wrap')
            btn_submit.click()

            # Вводим пароль
            txt_password = self._get_visible_elem(By.NAME, 'password')
            txt_password.send_keys(PASSWORD)

            # Нажимаем войти
            btn_submit = self._driver.find_element(By.CLASS_NAME, 'submit-button-wrap')
            btn_submit.click()

            # Ждем пока прогрузится первое письмо
            elem = self._get_visible_elem(By.XPATH, '//a[contains(@class, "js-letter-list-item")]')

            while True:
                # Список веб-элементов, соответствующих письмам: List[selenium.webdriver.remote.webelement.WebElement]
                letters = self._driver.find_elements(By.XPATH, '//a[contains(@class, "js-letter-list-item")]')
                # Извлекаем ссылки из веб-элементов, также превращаем его в множество, чтобы не было дублей
                links_subset = set([letter.get_attribute('href') for letter in letters])
                # Если собрали все ссылки, то выходим из цикла
                if links_subset.issubset(links):
                    break

                # Добавляем новые ссылки в общий список
                links.update(links_subset)

                actions = ActionChains(self._driver)
                actions.move_to_element(letters[-1])
                actions.perform()

                time.sleep(3)

        except Exception as e:
            print('Ошибка при сборе ссылок писем: ', str(e))
        finally:
            return list(links)

    def _parse_letters_links(self, links):
        """
        Парсит письма по ссылкам из списка links
        :param links: список ссылок, каждая из которых соответствует одному письму
        :type links: List[str]
        """
        for link in links:
            try:
                # Парсим письмо по ссылке
                self._parse_card(link)
                # Задержим на пару секунд
                time.sleep(3)
            except Exception as e:
                print(f'Ошибка парсинга страница: {link}: {e}')

    def _parse_card(self, link):
        """
        Парсит письмо по ссылке link
        :param link: ссылка письма
        :type link: str
        """
        self._driver.get(link)

        # Информация об отправителе
        elem = self._get_visible_elem(By.XPATH, '//span[contains(@class, "letter-contact")]')
        sender_mail = elem.get_attribute('title')
        sender_name = elem.text

        # Дата отправки
        elem = self._driver.find_element(By.CLASS_NAME, 'letter__date')
        letter_date = elem.text

        # Тема письма
        elem = self._driver.find_element(By.XPATH, '//h2[contains(@class, "thread-subject")]')
        letter_subject = elem.text

        # Текст письма
        letter_body_elem = self._driver.find_element(By.CLASS_NAME, 'letter__body')
        paragraphs = letter_body_elem.find_elements(By.TAG_NAME, 'p')
        letter_text = ' '.join([p.text for p in paragraphs])

        # Собираем информацию о письме в словарь
        letter = {
            'sender_name': sender_name,
            'sender_mail': sender_mail,
            'letter_date': letter_date,
            'letter_subject': letter_subject,
            'letter_text': letter_text
        }
        # Собираем созданные словари с информацией о письме в специальном атрибуте
        self._result.append(letter)

    def parse(self):
        # Список ссылок, каждая из которых соответствует одному письму
        links = self._get_letters_links()
        # Сохраняем ссылки в файл
        save_data_to_json('links.json', links)

        # Парсим ссылки писем
        self._parse_letters_links(links)

        self._driver.quit()


if __name__ == '__main__':
    # Парсер
    parser = MailRuParser()
    # Запускаем парсинг сайта
    parser.parse()

    # Сохраняем результат парсинга (список словарей) в файл
    parser.save_result_to_json('letters.json')
    # Добавляем полученный список писем в базу данных
    parser.save_result_to_db()
