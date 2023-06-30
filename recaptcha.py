from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from chromewebdriver import ChromeWebDriver
from selenium.webdriver.common.keys import Keys
from proxymanager import ProxyManager
from datetime import datetime
from time import *
PROCESS_NUMBER = 9
proxy = '38.153.201.194:8800'

scoreXPath = '//*[@id="score"]'

chromeWebDriver = ChromeWebDriver(PROCESS_NUMBER, proxy, 9)
chromeWebDriver.requestUrl('http://checkip.instantproxies.com')
sleep(3)
chromeWebDriver.requestUrl('https://ip-check.net/recaptchav3?format=text')
sleep(10)

score = chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, scoreXPath)), 10)
#print(score)
print(chromeWebDriver.getElementByXPath(scoreXPath).text)
sleep(10)
chromeWebDriver.close()
