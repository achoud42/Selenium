import time
import requests

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import undetected_chromedriver as uc
from constant import *

#proxy ='154.12.105.207:8800'
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")

# options.add_argument("--headless")


options.add_argument('--no-sandbox')
options.add_argument('--start-maximized')
options.add_argument('--start-fullscreen')
options.add_argument('--single-process')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--incognito")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("disable-infobars")
#options.add_argument('--proxy-server=%s' % proxy)
#print('Enter the gmailid and password')//*[@id="vin-form"]/div[1]/button/span[2]
#
def getRandomVin():
  #randomVinUrl = 'https://randomvin.com/getvin.php?type=real'
  vin = requests.get(randomVinUrl).text
  return vin

driver = webdriver.Chrome(ChromeDriverManager().install())
stealth(driver,
        languages=["en-US", "en"],   
        user_agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36',
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
def getdata(vin) :
  driver.get(carfaxUrl)
  driver.implicitly_wait(5)
  vinfield=driver.find_element(By.NAME, vinSearchXpath)
  vinfield.send_keys(vin)
  try:
    #cookies = '//*[@id="onetrust-accept-btn-handler"]'
    
    nextButton = driver.find_element("xpath",cookies)
    #nextButton.click()
    driver.execute_script("arguments[0].click();", nextButton)

    print("Accepted cookies")
  except:
    print("cookies not found")
  
  #arrow='//*[@id="__next"]/div/div/main/div/div[1]/div[1]/div/div/div/div/div/form/button/div'
  time.sleep(2)
  
  nextButton1 = driver.find_element("xpath",nextArrowXpath)
  nextButton1.click()
  #records = '//*[@id="__next"]/div/div/main/div/div[1]/div[2]/h1'
  print(vin)
  print(str(driver.find_element("xpath", recordsXpath).text).strip())

i = 0
while i < 1000:
  vin = getRandomVin()
  print(vin)
  try :
    getdata(vin)
  except :
    print("something went wrong for " + vin)
  i=i+1








