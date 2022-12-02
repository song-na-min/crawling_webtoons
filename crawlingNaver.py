import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import pandas as pd
from selenium.webdriver.common.by import By
#json
import json
from collections import OrderedDict

#mongoDB connect
from dotenv import load_dotenv
import os 
load_dotenv()
mongoDB = os.environ.get('mongoDB')
from pymongo import MongoClient
client = MongoClient(mongoDB)
db = client.test


URL = 'https://comic.naver.com/webtoon/weekday.nhn'
html = requests.get(URL).text # html 문서 전체를 긁어서 출력해줌, .text는 태그 제외하고 text만 출력되게 함
soup = BeautifulSoup(html, 'html.parser')

title = soup.find_all('a', {'class' : 'title'}) # a태그에서 class='title'인 html소스를 찾아 할당
id_list = [] ; title_list = [] ; author_list = [] ; day_list = [] ; genre_list = [] ; story_list = [] ; platform_list = []
num = 0
driver = webdriver.Chrome('C:/chromedriver.exe') # 크롬 사용하니까
driver.get(URL)

for i in range(len(title)):
    sleep(0.5) # 크롤링 중간 중간 텀을 주어 과부하 생기지 않도록

    page = driver.find_elements(By.CLASS_NAME,'title')
    page[i].click() #월요일 첫 번째 웹툰부터 순서대로 클릭

    sleep(0.5)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser') # 이동한 페이지 주소 읽고 파싱
    
    # 요일 수집
    day = soup.find_all('ul', {'class' : 'category_tab'})
    day = day[0].find('li', {'class' : 'on'}).text[0:1] 
    
    #title을 text로 변환
    t = title[i].text

    # 요일 두 개 이상이면 요일만 추가함
    if (t in title_list):  
        result = db.Webtoon.find_one({'title':t})
        #print(result['day'])
        day_update = result['day']+', ' + day
        #print(day_update)
        db.Webtoon.update_one({'title':t},{"$set":{'day':day_update}})
        driver.back()
        continue

    # 요일이 두개 이상인 것을 확인하기 위해 제목들을 리스트에 저장해놓는다.
    title_list.append(t)  # 제목 리스트에 추가

    author = soup.find_all('h2') # 두 번째 h2태그에 있음
    author = author[1].find('span', {'class' : 'wrt_nm'}).text[8:] # 7칸의 공백 후 8번 째부터 작가 이름임

    genre = soup.find('span', {'class' : 'genre'}).text # 장르 수집

    story = soup.find_all('p') # 줄거리 수집
    story = str(story[3])
    story = story.replace('<p>', '').replace('</p>', '').replace('<br/>', '\n') # <br>을 개행으로 바꾸기

    #현재 url출력
    #print(driver.current_url)
    #print("======")
    img=soup.find("div",class_="thumb")
    imgUrl=img.find("img")['src']
    #print(imgUrl)

    #DB에 저장할 data를 딕셔너리 형태로 저장
    file_data={}
    file_data["title"]=t
    #print(t)
    #print(type(t))
    file_data["creator"]=author
    #print(author)
    #print(type(author))
    file_data["description"]=story
    #print(story)
    #print(type(story))
    file_data["genre"]=genre
    #print(genre)
    #print(type(genre))
    file_data["header_img"]=imgUrl
    #print(imgUrl)
    #print(type(imgUrl))
    file_data["platform"]="naver"
    file_data["url"]=driver.current_url
    #print(driver.current_url)
    #print(type(driver.current_url))
    file_data["day"]=day
    #print(day)
    #print(type(day))
    file_data['isDeleted']=False
    print(file_data)

    # mongoDB에 해당 웹툰의 title이 있는지 확인한다. list로 바꾸는 이유는 길이를 확인하기 위해
    result = list(db.Webtoon.find({"title":t}))
    #print(type(result))
    #print(result)
    if len(result)==0:
        #없으면 db에 넣는다
        print("empty!")
        db.Webtoon.insert_one(file_data)
    else:
        #있으면 db에 넣지않고 지나간다.
        print("already in DB")

    driver.back() # 뒤로 가기