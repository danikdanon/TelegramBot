import requests
from bs4 import BeautifulSoup
import  re

def get_page(page_url) :
    response = requests.get(page_url)

    soup = BeautifulSoup(response.text, 'html.parser')

    main = soup.find('div', class_='mw-parser-output')

    p = main.findAll('p')

    # убираем лишнее
    p = str(p)  #привел к строке
    p = p.lower()
    reg = re.compile('[^а-яА-Я ]')
    p = reg.sub('', p)
    p = re.sub(r'\s+', ' ', p)
    p = p.replace('>', ' ')
    p = p.replace('<', ' ')


    list = p.split(' ')

    return list

