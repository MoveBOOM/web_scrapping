import requests
import bs4
import re
from fake_headers import Headers
import json
from tqdm import tqdm

headers = Headers(browser="firefox", os="win")

header_data = headers.generate()
vacancys = []
count = 0
count_false = 0

for page in tqdm(range(0, 39), desc='Выполняется поиск по страницам'):
    response = requests.get(
        f'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={page}', headers=header_data)

    html_data = response.text
    soup = bs4.BeautifulSoup(html_data, 'lxml')
    tag = soup.find_all('div', class_='serp-item')

    for mask in tag:
        lay = mask.find('a')
        link = lay['href']

        salary = 'Не указана'
        sal = mask.find('span', class_="bloko-header-section-2")
        if sal:
            gat = sal.text
            pattern = re.compile(r'\u202f')
            pattern1 = re.compile(r' руб.')  # Эта строка еще не работает
            repl = ' '
            salary = re.sub(pattern, repl, gat)

        name = mask.find(class_="bloko-header-section-3").text
        tex = mask.find('div', class_='vacancy-serp-item__meta-info-company').text
        company = re.sub(r'\s+', ' ', tex).strip()

        ci = mask.find('div', class_="vacancy-serp-item-company").text
        heh = re.findall(r'(?:Москва|Санкт-Петербург)', ci)
        city = heh[0] if heh else ''

        vacancy = {
            'link': link,
            'salary': salary,
            'company': company,
            'city': city,
            'name': name
        }

        response1 = requests.get(link, headers=header_data)
        html_data1 = response1.text
        soup1 = bs4.BeautifulSoup(html_data1, 'lxml')
        tag1 = soup1.find('div', class_='g-user-content')

        if tag1 is not None:
            text = tag1.text
            match = re.search(r'\b(Django|Flask)\b', text)
            if match:
                match_word = match.group(0)
                vacancys.append(vacancy)
                count += 1
            else:
                count_false += 1
        else:
            continue

# Записываем в файл результат парсинга с сохранением кодировки UTF-8
filename = 'data.json'
with open(filename, 'w', encoding='utf-8') as file:
    json.dump(vacancys, file, indent=4, ensure_ascii=False)

print(f'Количество записанных вакансий - {count}')
print(f'Количество не подходящих вакансий - {count_false}')