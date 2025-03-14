from celery import Celery, Task
import requests
from bs4 import BeautifulSoup
import xmltodict
import time


# Настройка Celery
app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')



class FetchLinksTask(Task):
    def run(self, url):
        alllinks = []
        domen = "https://zakupki.gov.ru"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }
        time.sleep(1)
        response = requests.get(url, headers=headers)

        # Проверяем, успешен ли запрос
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # alllinks = []
            # Находим все div с классом "row"
            rows = soup.find_all('div', class_='row no-gutters registry-entry__form mr-0')
            # Перебираем найденные строки и извлекаем вторую ссылку
            for row in rows:
                # Находим нужный div внутри каждой строки
                icon_div = row.find('div', class_='w-space-nowrap ml-auto registry-entry__header-top__icon')
                if icon_div:
                    # Находим все ссылки внутри этого div
                    links = icon_div.find_all('a')
                    # Проверяем, есть ли вторая ссылка
                    if len(links) > 1:
                        second_link = links[1].get('href')  # Получаем href второй ссылки
                        # print(second_link)  # Выводим вторую ссылку
                        new_url = domen + second_link.replace('view.html', 'viewXml.html')
                        alllinks.append(new_url)
        else:
            print(f"Ошибка при получении страницы. Статус код: {response.status_code} Загружаемый адрес: {url}")
        return alllinks


class FetchXMLTask(Task):
    def run(self, link):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }
        # Загружаем содержимое страницы
        time.sleep(2)
        response = requests.get(link, headers=headers)
        # выдержка паузы между загрузкой страниц

        # Проверяем успешность запроса
        if response.status_code == 200:
            try:
                # Парсим XML с помощью xmltodict
                xml_data = xmltodict.parse(response.content)

                root_key = list(xml_data.keys())[0]
                # Извлечение данных
                item = xml_data[root_key]['commonInfo']['publishDTInEIS']
                if (item):
                    publish_date = item
                else:
                    publish_date = 'None'

                #return publish_date
                return [link, publish_date]
            except Exception as e:
                print("Ошибка при разборе XML:", e)

        else:
            print(f"Ошибка при загрузке страницы: {response.status_code} Загружаемый адрес: {link}")


@app.task(bind=True)
def fetch_links(self, url):
    links = FetchLinksTask().run(url)
    return links

@app.task(bind=True)
def fetch_xml(self, link):
    publish_date = FetchXMLTask().run(link)
    return publish_date

