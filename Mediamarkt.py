from selenium import webdriver as wd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import re
import time
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import os

options = Options()


options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

url='https://www.mediamarkt.de/de/product/_samsung-gq49q70rgtxzg-2530685.html'



driver=wd.Chrome(executable_path = 'C://chromedriver.exe',chrome_options=options)
driver.get(url)
driver.implicitly_wait(10)


res=driver.page_source
html=BeautifulSoup(res,'html.parser')

product=html.find('h1',{'class':'mms-headline'})
if "LG" in product:
    productName=product.text[:10]
elif "SONY" in product:
    productName=product.text[:14]
else:
    productName=product.text[:18]

number=driver.find_element_by_xpath('//*[@id="rootWrapper"]/div/div/div[3]/div/div/div[1]/a/span').text
num=number.split(' ')
num_of_reviews=int(num[0])



date_list=[]
title_list=[]
rating_list=[]
body=[]
i=1

try:
    while len(date_list)<=num_of_reviews:
    
        bsobj=driver.page_source
        bs_obj=BeautifulSoup(bsobj,"html.parser")

        Date=bs_obj.findAll('span',{'class':'mms-review-head__date'})
        for i in range(len(Date)):
            date_list.append(Date[i].text)

        title=bs_obj.findAll('strong',{'class':'mms-headline'})
        for j in range(len(title)):
            title_list.append(title[j].text)

        description=bs_obj.findAll('p',{'itemprop':'description'})
        for h in range(len(description)):
            body.append(description[h].text)

        reviews=bs_obj.findAll('div',{'class':'mms-review'})
        obj=pd.DataFrame(reviews)
        for u in range(len(obj)):
            rating_list.append(str(obj[0][u]).count('#DF0000'))


        #next=bs_obj.findAll('div',{'class':'reviews-pagination-wrapper'})
        if len(date_list)<=10:
            driver.find_element_by_xpath('//*[@id="reviews"]/div[2]/div/div/div/div[12]/button').send_keys(Keys.ENTER)
        elif len(date_list)>10:
            driver.find_element_by_xpath('//*[@id="reviews"]/div[2]/div/div/div/div[12]/button[2]').send_keys(Keys.ENTER)


        try:
            WebDriverWait(driver, 15).until(
                # 지정한 한개 요소가 올라면 웨이트 종료
                EC.presence_of_element_located((By.XPATH, '//*[@id="reviews"]/div[2]/div/div/div/div[12]/button[2]'))
            )
        except Exception as e:
            print( '오류 발생', e)

        time.sleep(3)

except: 
    driver.close()
    driver.quit()
    
rating_final=pd.DataFrame(rating_list,columns=['Rating'])
title_final=pd.DataFrame(title_list,columns=['Title'])
Date_final=pd.DataFrame(date_list,columns=['Date'])
body_final=pd.DataFrame(body,columns=['body'])
final=pd.concat([rating_final,Date_final,title_final,body_final],axis=1)

from datetime import datetime
month=[]
year=[]
for x in final['Date']:
    month.append(datetime.strptime(x,'%d.%m.%Y').month)
    year.append(datetime.strptime(x,'%d.%m.%Y').year)
    
    
format_date=[]
for xy in final['Date']:
    format_date.append(datetime.strftime(datetime.strptime(xy,'%d.%m.%Y'),'%m/%d/%Y'))
    

final['Month']=month
final['Year']=year
final['Date']=format_date
final['Retailer']='Media Markt'
final['Country']='DE'

