from flask import Blueprint, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
import time
from pyvirtualdisplay import Display

bp = Blueprint('main', __name__, url_prefix='/')

display = Display(visible=0, size=(1920, 1080))
display.start()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

#chrome_options.add_argument('headless')
#chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("lang=ko_KR")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/clock')
def clock():
    return render_template('clock.html')


@bp.route('/stock', methods=['POST'])
def stock():
    data = request.get_json()
    code1 = data['code1']
    code2 = data['code2']
    code3 = data['code3']

    company_codes = []
    company_codes.append(code1)
    company_codes.append(code2)
    company_codes.append(code3)

    prices = selenium_price(company_codes)

    #prices = []
    #for item in company_codes:
    #    now_price = selenium_price(item)
    #    prices.append(now_price)

    sise = {
        'code1': prices[0], 'code2': prices[1], 'code3': prices[2]
    }

    return jsonify(result2= "ok", result3= sise, now= datetime.today())

def bs4_price(company_code):
    bs_obj = get_bsoup(company_code)
    no_today = bs_obj.find("p", {"class": "no_today"})
    blind = no_today.find("span", {"class": "blind"})

    now_price = blind.text
    return now_price

def get_bsoup(company_code):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    url = "https://finance.naver.com/item/main.nhn?code=" + company_code

    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        bs_obj = BeautifulSoup(result.content, "html.parser")
        return bs_obj
    else:
        print(result.status_code)

def selenium_price(company_codes):
    path = '/home/ubuntu/chromedriver'
    driver = webdriver.Chrome(path, chrome_options=chrome_options)
    # driver = webdriver.Chrome('/selenium/chromedriver', chrome_options=chrome_options)
    driver.implicitly_wait(10)

    prices = []
    for code in company_codes:
        url = 'https://m.kbsec.com/go.able?linkcd=m04010000&flag=0&JmGb=K&stockcode=' + code
        driver.get(url)
        driver.implicitly_wait(10)

        select = '#container > form > div.stockInfoBox > div:nth-child(1) > div.cellL.stockToday.stockUp > strong'
        time.sleep(1)
        selected = driver.find_element_by_css_selector(select)

        now_price = selected.text
        prices.append(now_price)

    return prices



