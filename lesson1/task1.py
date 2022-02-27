# Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.
import requests
import json

# Имя пользователя на github, для которого необходимо вывести список его репозиториев
user_name = 'lkamalt'

# Делаем запрос на получение списка репозиториев заданного пользователя
url = f'https://api.github.com/users/{user_name}/repos'
response = requests.get(url)

# Записываем результат в json-файл
with open('repos.json', 'w', encoding='utf8') as f:
    json.dump(response.json(), f)
