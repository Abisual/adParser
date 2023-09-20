import re
import requests
from lxml import html
import time
import random
import sqlite3
from datetime import datetime
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
            unique_id TEXT,
            timestamp DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME')),
            archived BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()



def insert_into_db(conn, data, unique_id, timestamp):
    cursor = conn.cursor()

    # Помечаем все объявления с таким же query как архивированные
    cursor.execute('''
        UPDATE ads
        SET archived=1
        WHERE unique_id NOT IN (
            SELECT unique_id FROM ads WHERE query=?
        )
    ''', (query,))
    conn.commit()

    # Далее проверяем, есть ли уже в базе данных объявление с таким же unique_id
    cursor.execute("SELECT * FROM ads WHERE unique_id=?", (unique_id,))
    existing_data = cursor.fetchone()

    if existing_data:
        # Если объявление с таким unique_id уже есть в базе, сравниваем данные
        if (
                existing_data[1] != data['title'] or
                existing_data[2] != data['price'] or
                existing_data[3] != data['link'] or
                existing_data[4] != data['description']
        ):
            # Собираем информацию о том, что изменилось
            changes = []
            if existing_data[1] != data['title']:
                changes.append(f"Название: '{existing_data[1]}' -> '{data['title']}'")
            if existing_data[2] != data['price']:
                changes.append(f"Цена: '{existing_data[2]}' -> '{data['price']}'")
            if existing_data[3] != data['link']:
                changes.append(f"Ссылка: '{existing_data[3]}' -> '{data['link']}'")
            if existing_data[4] != data['description']:
                changes.append(f"Описание: '{existing_data[4]}' -> '{data['description']}'")

            change_info = "\n  ".join(changes)

            # Если хотя бы одно поле изменилось, обновляем данные
            cursor.execute('''
                UPDATE ads
                SET title=?, price=?, link=?, description=?, query=?, unique_id=?, timestamp=?, archived=0
                WHERE unique_id=?
            ''', (
            data['title'], data['price'], data['link'], data['description'], query, unique_id, timestamp, unique_id))
            conn.commit()
            print(f"Объявление с unique_id {unique_id} обновлено в базе данных. Изменения:\n  {change_info}")
        else:
            print(f"Объявление с unique_id {unique_id} не изменилось.")
    else:
        # Если объявление с таким unique_id не существует, вставляем его
        cursor.execute('''
            INSERT INTO ads (title, price, link, description, query, unique_id, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['title'], data['price'], data['link'], data['description'], query, unique_id, timestamp))
        conn.commit()
        print(f"Добавлено новое объявление с unique_id {unique_id}.")


def parse_drom(query):
    base_url = f"https://auto.drom.ru/search{query}"
    current_page = 1  # Текущая страница

    headers = {
        "User-Agent": random.choice(user_agents)
    }

    # Создаем одно подключение к базе данных перед началом цикла
    conn = sqlite3.connect("ads.db")
    create_table(conn)

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

                    # Получаем текущую временную метку
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Используем созданное подключение для вставки данных в базу
                    insert_into_db(conn, data, unique_id, timestamp)

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

    # Закрываем подключение к базе данных после завершения цикла
    conn.close()

print("Начинаем парсинг сайта Drom.ru")
parse_drom(query)
