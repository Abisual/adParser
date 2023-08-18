import re
import requests
from lxml import html
import time
import random
import sqlite3
from urllib.parse import urljoin
from config import query, container_xpath, title_xpath, price_xpath, link_xpath, \
    description_xpath, description_parts_xpath, user_agents

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY,
            title TEXT,
            price TEXT,
            link TEXT,
            description TEXT,
            query TEXT,
            unique_id TEXT
        )
    ''')
    conn.commit()

def insert_into_db(conn, data, unique_id):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ads (title, price, link, description, query, unique_id) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['title'], data['price'], data['link'], data['description'], query, unique_id))
    conn.commit()

def parse_drom(query):
    base_url = f"https://auto.drom.ru/search{query}"
    current_page = 1  # Текущая страница

    headers = {
        "User-Agent": random.choice(user_agents)
    }

    while True:
        page_url = urljoin(base_url, f"page{current_page}/")
        print(f"Отправляем запрос на страницу {page_url}")
        response = requests.get(page_url, headers=headers)

        if response.status_code == 200:
            soup = html.fromstring(response.content)

            # Ищем контейнер с объявлениями
            container = soup.xpath(container_xpath)

            if container:
                container = container[0]  # Выбираем первый элемент, если он найден

                # Используем XPath для извлечения описаний
                description_divs = container.xpath(description_xpath)
                descriptions = []
                for desc_div in description_divs:
                    description_parts = desc_div.xpath(description_parts_xpath)
                    description = " ".join(description_parts)
                    descriptions.append(description.strip())

                # Используем XPath для извлечения заголовков, цен и ссылок
                titles = container.xpath(title_xpath)
                price_elems = container.xpath(price_xpath)
                link_elems = container.xpath(link_xpath)

                results = []

                for title_elem, price_elem, link_elem, description in zip(titles, price_elems, link_elems, descriptions):
                    title = title_elem.text.strip()  # Получаем текст из HtmlElement
                    price = price_elem.text.strip()  # Получаем текст из HtmlElement
                    link = link_elem.get("href")  # Получаем ссылку

                    unique_id_match = re.search(r'(\d+)\.html', link)
                    if unique_id_match:
                        unique_id = unique_id_match.group(1)
                    else:
                        unique_id = ""

                    data = {"title": title, "price": price, "link": link, "description": description}
                    results.append(data)

                    conn = sqlite3.connect("ads.db")
                    create_table(conn)
                    insert_into_db(conn, data, unique_id)
                    conn.close()

                if results:
                    print(f"Результаты парсинга со страницы {current_page}:")
                    for idx, item in enumerate(results, 1):
                        print(f"Объявление {idx}:")
                        print("  Название:", item["title"])
                        print("  Цена:", item["price"])
                        print("  Описание:", item["description"])
                        print("  Ссылка:", item["link"])
                        print("=" * 30)

                    current_page += 1  # Переходим на следующую страницу
                    random_sleep = random.uniform(3, 8)  # Случайный таймаут от 3 до 8 секунд
                    print(f"Ждем {random_sleep:.2f} секунд перед следующим запросом...")
                    time.sleep(random_sleep)  # Случайная пауза
                else:
                    print("На странице нет объявлений, парсинг завершен.")
                    break
            else:
                print("Контейнер с объявлениями не найден. Парсинг завершен.")
                break
        else:
            print("Ошибка при выполнении запроса. Код ответа:", response.status_code)
            break

print("Начинаем парсинг сайта Drom.ru")
parse_drom(query)
