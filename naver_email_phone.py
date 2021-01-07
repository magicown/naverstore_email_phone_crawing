# -*- conding: utf-8 -*-
import os, sys
from selenium import webdriver
import urllib.request
from urllib.request import urlopen
from urllib import parse
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook
from openpyxl import load_workbook
import pyautogui as pg
import csv

def chrome_option():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument("lang=ko_KR") # 한국어!
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    return options

#상품 명
def get_email_phone(soup):

    # 상품명
    try : 
        title = soup.select_one('._2bY0n46Os8')    
        email = title.get_text()

        text = soup.select_one('.WIgpnRinBM')
        text = text.get_text()
        text = text.replace('고객센터: ','')
        text = text.replace('인증잘못된 번호 신고','')
    
        # print(email + ' : ' + text)

        return email, text
    except :
        pass
    
    

def make_total_page(soup):
    total_text = soup.select_one('.subFilter_num__2x0jq')
    tt = total_text.get_text()
    t_cnt = tt.replace(",","")
    total_cnt = int(int(t_cnt)/5)

    return total_cnt


options = chrome_option()
total = 1
words = ""
keyword = pg.prompt(title='키워드를 입력하세요.', default='키워드는 콤마로 구분해주세요.')
kw = keyword.split(',')

# print(os.path)
# 엑셀 시트에 추가하기 위해서 선언한다.
# wb = load_workbook('./email_phone.xlsx')
# ws = wb.active
cnt = 0
# pg.confirm('데이터를 수집합니다.')
# app = QApplication(sys.argv)
# ex = MyApp()
prog_cnt = 1
rem_cnt = 0
searchList = []
for key_text in kw :
    words = parse.quote_plus(key_text)   

    url = 'https://search.shopping.naver.com/search/all?frm=NVSHCHK&npayType=2&origQuery='+words+'&pagingIndex=1&pagingSize=5&productSet=checkout&query='+words+'&sort=rel&timestamp=&viewType=thumb'
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')

    #전체 페이지 갯수를 만든다.
    total_cnt = make_total_page(soup)
    rem_cnt = total_cnt
    print("전체갯수 : "+str(total_cnt))
    
    start = 1
    while start <= total_cnt:
        URL = "https://search.shopping.naver.com/search/all?frm=NVSHCHK&npayType=2&origQuery="+words+"&pagingIndex="+str(start)+"&pagingSize=5&productSet=checkout&query="+words+"&sort=rel&timestamp=&viewType=thumb"   
        if  getattr(sys, 'frozen', False): 
            chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
            driver = webdriver.Chrome(chromedriver_path, options=options)
        else:
            driver = webdriver.Chrome(options=options) 
        # driver = webdriver.Chrome(executable_path='chromedriver', options=options)
        driver.get(url=URL)
        try :
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "thumbnail_thumb__3Agq6"))
            )        
        finally :
            html_doc = driver.page_source        
            soup = BeautifulSoup(html_doc, 'html.parser')

            #리스트에서 url을 가져온다.
            list_div = soup.select('.imgList_title__3yJlT')           
            k = 1    
            for i in list_div :        
                for tag in i.findAll('a', href=True):
                    temp = []
                    URL1 = tag['href']
                    if  getattr(sys, 'frozen', False): 
                        chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
                        driver1 = webdriver.Chrome(chromedriver_path, options=options)
                    else:
                        driver1 = webdriver.Chrome(options=options)

                    driver1.get(url=URL1)
                    try:
                        element = WebDriverWait(driver1, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "_2bY0n46Os8"))
                        )
                    except:
                        pass
                    finally:                                    
                        html_doc = driver1.page_source
                        soup1 = BeautifulSoup(html_doc, 'html.parser')
                        # title = get_email_phone(soup1)   
                        # 상품명
                        try : 
                            title = soup1.select_one('._2bY0n46Os8')    
                            email = title.get_text()

                            text = soup1.select_one('.WIgpnRinBM')
                            text = text.get_text()
                            text = text.replace('고객센터: ','')
                            text = text.replace('인증잘못된 번호 신고','')
                        
                            # temp.append(key_text)
                            # temp.append(email)
                            # temp.append(text)
                            # searchList.append(temp)

                            print('진행갯수 : '+str(prog_cnt) +  ' / 남은갯수 : '+str(total_cnt-prog_cnt) +' --  '+email + ' : ' + text)


                            f = open('storeSaveEmailPhone.csv','a',encoding='utf-8', newline='')
                            csvWriter = csv.writer(f)                            
                            csvWriter.writerow([key_text,email,text])
                            f.close()
                            # print(searchList)
                            

                            # return email, text
                        except :
                            pass
                        
                        
                        k += 1
                        prog_cnt += 1
                       
            cnt += 1
            start += 1
            

pg.alert('데이터 수집이 완료되었습니다.')

# pyinstaller --nowindowed --add-binary="chromedriver.exe";"." naver_email_phone.py