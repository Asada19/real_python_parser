"""
Тестовое задание

Создайте Python-приложение, которое будет парсить определенные веб-сайты и извлекать из них информацию. Ваше приложение должно выполнять следующие функции:

1. Получить список статей с главной страницы сайта
    [https://realpython.com/search?kind=article&level=basics] и сохранить следующую информацию в структурированном виде JSON:
    - Заголовок статьи
    - URL-ссылка на статью
    - Дата публикации
    - Теги
    - Краткое содержание статьи
2. Для каждой статьи из списка необходимо перейти по ссылке и скачать полный текст статьи, извлекая только основное содержимое, без навигационных элементов, рекламы и комментариев.
3. Разделять страницы сайта на полные от режима предпросмотра .
4. Для страниц в режиме предпросмотра необходимо помечать их флагом.
5. Если в блоке текста находятся дополнительные ссылки их нужно так же отдельно разместить в JSON к каждой секции и отдельным списком ко всему документу.
6. Текст каждой секции должен храниться отдельной записью.
7. Сохраните полученную информацию в виде JSON-файла, где каждый элемент списка представляет собой структурированные данные об одной статье.

Оценка кандидатов будет производиться на основе следующих критериев:

- Качество и чистота кода
- Эффективность алгоритмов и структур данных
- Обработка исключений и ошибок
- Способность извлекать информацию корректно и точно
"""

import os
import json
import time
from selenium import webdriver
from dotenv import load_dotenv
from datetime import datetime

start = datetime.now()
load_dotenv()

EMAIL = os.getenv('RP_EMAIL')
PASSWORD = os.getenv('RP_PASSWORD')

driver = webdriver.Chrome()
URL = 'https://realpython.com/search?kind=article&level=basics'
driver.get(URL)


def login_to_website(mail, password):
    login_url = driver.find_element('css selector', '.btn.text-light').get_attribute('href')
    try:
        driver.get(login_url)
        email_field = driver.find_element('id', 'id_login')
        email_field.send_keys(mail)
        password_field = driver.find_element('id', 'id_password')
        password_field.send_keys(password)
        driver.find_element('name', 'jsSubmitButton').click()

    except:
        raise Exception('Login Error')


login_to_website(EMAIL, PASSWORD)
driver.get(URL)
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    articles = driver.find_elements('css selector', ".container.my-3")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

res_list = []

for article in articles:

    title = article.find_element("tag name", 'h2')
    link = article.find_element('class name', 'stretched-link').get_attribute('href')
    publish_date = article.find_element('tag name', 'span')
    tags = article.find_element('css selector', ".small.text-muted.my-0")
    description = article.find_element("css selector", '.text-muted.my-0.mt-1.small')

    res_list.append({
        'title': title.text,
        'link': link,
        'publish_date': publish_date.text,
        'tags': [i.text for i in tags.find_elements('tag name', 'a')],
        'description': description.text,
        'preview': False,
        'full_article': '',
        'additional_links': []
        })


for item in res_list:
    driver.get(item['link'])

    if 'preview' in driver.current_url:
        item['preview'] = True

    content = driver.find_element('class name', 'article-body')

    # Удаление навигационных элементов
    driver.execute_script("""
        const elements = [...document.querySelectorAll('div > .bg-light.sidebar-module.sidebar-module-inset'),
                        ...document.querySelectorAll('div > .sidebar-module.sidebar-module-inset.p-0')]
        for (let i = 0; i < elements.length; i++) {
            elements[i].remove();
            }
    """)

    # Удаление рекламы
    driver.execute_script("""
            const elements = document.querySelectorAll('a > .small.text-muted')
            for (let i = 0; i < elements.length; i++) {
                elements[i].remove();
                }
        """)

    item['full_article'] = content.text.replace('Remove ads', '')
    item['additional_links'] = [{'link_text': i.text,
                                 'link_url': i.get_attribute('href')}
                                for i in content.find_elements('tag name', 'a') if i.text not in ['', 'Remove ads', 'remove_ads']]
    time.sleep(1)


with open('tests.json', 'w') as article:
    json.dump(res_list, article, ensure_ascii=False, indent=4)

driver.quit()
print(datetime.now() - start)