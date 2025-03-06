import requests
from bs4 import BeautifulSoup
import xmltodict
import time

#это список извлеченных номеров
pubeis = []

def parse_page(url):
    #url = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber=1'
    domen = "https://zakupki.gov.ru"
    response = requests.get(url)
    # Проверяем, успешен ли запрос
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        alllinks = []
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
                    #print(second_link)  # Выводим вторую ссылку
                    new_url = domen + second_link.replace('view.html', 'viewXml.html')
                    alllinks.append(new_url)

        #это список извлеченных номеров
        #pubeis = []

        for link in alllinks:
            # Загружаем содержимое страницы
            response = requests.get(link)
            #выдержка паузы между загрузкой страниц
            time.sleep(1)
            # Проверяем успешность запроса
            if response.status_code == 200:
                try:
                    # Парсим XML с помощью xmltodict
                    xml_data = xmltodict.parse(response.content)

                    root_key = list(xml_data.keys())[0]
                    # Извлечение данных
                    item = xml_data[root_key]['commonInfo']['publishDTInEIS']
                    if (item):
                        pubeis.append(item)
                    else:
                        pubeis.append('None')



                except Exception as e:
                    print("Ошибка при разборе XML:", e)

            else:
                print(f"Ошибка при загрузке страницы: {response.status_code} Загружаемый адрес: {link}")

    else:
        print(f"Ошибка при получении страницы. Статус код: {response.status_code}")







if __name__ == '__main__':
    parsedpages = ['1','2']
    templatepage = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber='

    for num in parsedpages:
        scanpage = templatepage+num;
        parse_page(scanpage)

    # вывод списка номеров
    print(pubeis)


