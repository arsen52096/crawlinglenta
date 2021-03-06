__author__ = 'arsen52096'

import requests
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd
import os




def date_run(url: str) -> list:
    """
    
    take url, 
    
    get date and manipulate this date to string

    return: url link with date (string)

    first day of lenta is 31.08.1999

    """

    date_first_day_lenta = datetime.date(2019,2,5)
    date_today = datetime.date.today()
    delta = date_today - date_first_day_lenta
    
    date_list = [
        date_first_day_lenta + datetime.timedelta(
        days = x
    ) for x in range(0, int(str(delta)[0:2]))
    ]

    formating_date_list = [
        datetime.datetime.strptime(
            str(date), '%Y-%m-%d'
        ).strftime('%Y/%m/%d/') 
        for date in date_list
    ]
    
    return [url + date for date in formating_date_list]


def get_html(date_run_url: list) -> list:
    """take url with date 

    and return all links of lenta.ru """

    links = set()
    for date_url in range(len(date_run_url)):
        page = requests.get(date_run_url[date_url])
        soup = BeautifulSoup(page.content, 'html.parser')

        year = int(date_run_url[date_url][17:21])

        if year==1999:
            for link in soup.find(attrs={
                'class':"page-archive"
                }).findAll('a', attrs={'href': re.compile("news/1999")}):
                links.add('https://lenta.ru'+link.get('href'))
        elif year>=2000:
            for link in soup.find(attrs={
                'class':"page-archive"
                }).findAll('a', attrs={'href': re.compile("news/20")}):
                links.add('https://lenta.ru'+link.get('href'))
        
    return links



def article_text(urls: list, genres):

    """
    take all links of lenta.ru, 
    processing that
    return excel table with date, genre, title list and body article
    

    """
    
    date_list = []
    genre_list = []
    article_title_list = []
    body_list = []
    
    for url in urls:
        
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
         
        date = soup.find(attrs={'itemprop' : 'datePublished'}).text[1:]
        date_list.append(date)
        
        article_title = soup.title.string
        article_title_list.append(article_title)
        
        genr = ', '.join([genres[slovo] for slovo in range(len(genres)) if genres[slovo] in article_title])
        genre_list.append(genr)
        
        
        article_text = soup.find(attrs={'itemprop' : 'articleBody'}).find_all('p')
        article_text = [p_section.text.strip() for p_section in article_text] #if p_section.contents[0].name==None]
        body = ' '.join(article_text)
        body_list.append(body)
        
    data_lenta = {
        'Date': date_list,
        'genre': genre_list,
        'title': article_title_list,
        'article_test': body_list,
    }

    return data_lenta


if __name__ == '__main__':

    url = 'https://lenta.ru/'
    
    genres = ['Мир', 'Бывший СССР', 'Россия', 'Экономика', 'Силовые структуры', 'Наука и техника', 
        'Культура', 'Спорт', 'Интернет и СМИ', 'Ценности', 'Путешествия', 'Из жизни', 'Дом']


    url_date = date_run(url)
    html = get_html(url_date)
    article_text = article_text(html, genres)
    general_dataframe = pd.DataFrame(article_text)[['Date', 'genre', 'title', 'article_test']]

    writer = pd.ExcelWriter('lenta.xlsx')
    general_dataframe.to_excel(writer)
    writer.save()




    # general_dataframe = pd.DataFrame(
    #     article_text(
    #         get_html(
    #             date_run(url)
    #             ), genres
    #         )
    # )[['Date', 'genre', 'title', 'article_test']]

    

