from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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


options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches",["enable-logging"])
url = 'https://webtoon.kakao.com/original-webtoon?'
week = ['tab=mon', 'tab=tue', 'tab=wed', 'tab=thu', 'tab=fri', 'tab=sat', 'tab=sun']
title_list = [] ; id_list = [] ; author_list = [] ;  day_list = []  ; genre_list = [] ; story_list = [] ; platform_list = []
num = 366 # 네이버 웹툰 id가 365까지였음

URL = url
driver = webdriver.Chrome('C:/chromedriver.exe',options=options)
driver.get(URL) #요일별로 링크 가져옴

sleep(1)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser') # 제목, 작가, 요일 긁어오기 위해 현재 페이지 파싱

title = soup.find_all('img', {'class': 'w-full mx-auto my-0'}) # 제목 수집
p = 0 # 첫 번째 작품 링크부터 들어가기 위해
page=soup.find_all('a', {'class': 'w-full h-full relative overflow-hidden before:absolute before:inset-0 before:bg-grey-01 before:-z-1'})
for j in range(len(title)):
    t = title[j]["alt"]
    sleep(1)
    print("------webtoon-----------")
    print(t)
    result = list(db.Webtoon.find({"title":t}))
    if len(result)==0:
        print("empty!")
    else:
        print("already in DB")
        continue
    url = 'https://webtoon.kakao.com'+page[p]['href']
    print(url)
    driver.get(url)
    webtoon_id=url.split('/')[5]
    print(webtoon_id)
    if(driver.current_url=="https://webtoon.kakao.com/"):
        print("adult!!!!")
        p+=1
        continue
    p += 1
    sleep(1)
    print("------meta-----------")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, 'overflow-hidden.cursor-pointer')
        )
    )

    #상세페이지로 이동
    css_selector = 'overflow-hidden.cursor-pointer'
    element = driver.find_element(By.CLASS_NAME,css_selector)
    print(type(element))
    element.click()
    sleep(2)
    day_list=driver.find_elements(By.CSS_SELECTOR,"#root > main > div > div.page.bg-background.activePage > div > div.h-full.overflow-hidden.w-full.z-1.fixed.inset-0.bg-dark-background > div.relative.z-1.h-full > div > div > div.swiper-slide.swiper-no-swiping.swiper-slide-active > div > div.relative.h-full > div > div > div.swiper-slide.swiper-slide-active > div > div > div > div > div.flex.flex-wrap > p.whitespace-pre-wrap.break-all.break-words.support-break-word.font-badge.\!whitespace-nowrap.mr-4.s11-bold-black.bg-white.px-6")
    day=''
    for date in day_list:
        day=day+date.text+','
    day = day[:-1]
    # day= ",".join(day)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser') # 장르, 줄거리 가져오기 위해 현재 페이지 파싱
    sleep(2)
    print(day)

    #줄거리
    print("story")
    story = soup.find('meta', {'name' : 'twitter:description'}) # 줄거리 수집
    story_list.append(story) # 줄거리 리스트에 추가
    print(story['content'])
    print(type(story['content']))
    #이미지 링크
    #print("img")
    img= soup.find('meta',{'name':'twitter:image'})
    #print(img['content'])
    #print(type(img['content']))

    meta= soup.find('script',{'id':"__NEXT_DATA__"}).text
    meta_json = json.loads(meta)

    author = meta_json['props']['initialState']['content']['contentMap'][webtoon_id]['authors']
    #print("author")
    #print(author)
    story = meta_json[]
    genre = meta_json['props']['initialState']['content']['contentMap'][webtoon_id]['genre']
    #print(genre)
    file_data={}
    file_data["title"]=t
    print(t)
    print(type(t))
    file_data["creator"]=author
    print(author)
    print(type(author))
    file_data["description"]=story['content']
    print(story['content'])
    print(type(story['content']))
    file_data["genre"]=genre
    print(genre)
    print(type(genre))
    file_data["header_img"]=img['content']
    print(img['content'])
    print(type(img['content']))
    file_data["platform"]="kakao"
    file_data["url"]=driver.current_url
    print(driver.current_url)
    print(type(driver.current_url))
    file_data["day"]=day
    print(day)
    print(type(day))
    file_data['isDeleted']=False
    print(file_data)
    db.Webtoon.insert_one(file_data)

    num+=1
    sleep(3)