from tasks import fetch_links, fetch_xml
from celery import group, chain

if __name__ == "__main__":
    links = []

    # Сбор ссылок с первой и второй страниц
    for page in range(1, 3):
        templatepage = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber='
        scanpage = templatepage + str(page)
        #links = fetch_links.delay(scanpage)
        links.append(scanpage)

    # Создаем группу задач
    job = group(fetch_links.s(link) for link in links)
    # Запускаем задачи и ждем завершения
    result = job.apply_async()

    # Перебираем результаты по мере их готовности
    for res in result:
        res_result = res.get(timeout=10)  # Получить результат задачи

        # Это второй вариант реализации, когда функция парсинга возращает список с ссылкой
        # и извлеченым параметром

        # Создаем группу задач
        jobparse = group(fetch_xml.s(parse_url) for parse_url in res_result)
        # Запускаем задачи и ждем завершения
        parseresult = jobparse.apply_async()
        # Перебираем результаты по мере их готовности
        for parseres in parseresult:
            spisok = parseres.get(timeout=10)
            print(spisok)


        #это первый вариант реализации, в котором функция парсинга возращает только код
        #for parse_url in res_result:
        #    res_kod = fetch_xml.delay(parse_url)
        #    kod = res_kod.get()
        #    print("parse url=" + parse_url + " , extract cod=" + kod)



