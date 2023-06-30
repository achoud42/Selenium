# http://vautoextract.vindb.org//licenseapi.php?key=24GCRN4UT2TIZIS&plate=TT42Q23&state=GA
# http://docs.autoscale.ventures/pages/viewpage.action?pageId=35127548&fbclid=IwAR3_dEul46F7PRbZ24-9ts9kgVmvim4YgTd2MgwH1qAp5mIEOE845Olxds0
import selenium
import time
import os
import shutil
import psutil
import traceback
import json
import seleniumwire
from seleniumwire import webdriver
from gzip import decompress

from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


class FireFoxWebDriver:
  DRIVER_PATH = '/home/licensesearch/chromedrivers/v92/chromedriver'
  DEBUG_PATH = '/home/licensesearch/webdriver_debug/'
  
  def __init__(self, index, proxy, startindex):
    index = index + startindex
    self.index = index
    self.screenshotCount = 0    
    self.stats = {
      'request_url': 0,
      'click_element': 0,
      'exception': 0
    }
    self.paths = {
      'userdata': self.DEBUG_PATH + 'userdata/' + str(self.index) + '/',
      'logs': self.DEBUG_PATH + 'logs/' + str(self.index) + '/',
      'screenshots': self.DEBUG_PATH + 'screenshots/' + str(self.index) + '/'}
     
    self.driver = None
    self.port = str(30000 + int(index))
    self.error = None
    self.usageCount = 0
    self.proxy = proxy

    # Configure Proxy Option
    prox = Proxy()
    prox.proxy_type = ProxyType.MANUAL

    # Proxy IP & Port
    prox.http_proxy = proxy 
    prox.ssl_proxy = proxy 

    # Configure capabilities 
    capabilities = webdriver.DesiredCapabilities.FIREFOX
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

    capabilities['proxy'] = {
      'httpProxy': self.proxy,
      'ftpProxy': self.proxy,
      'sslProxy': self.proxy,
      'proxyType': 'MANUAL',
    }
    self.close() # kill previous instances
    #firefoxOptions = webdriver.FirefoxOptions()

    firefoxOptions = webdriver.FirefoxOptions()
    #firefoxOptions.add_argument('--headless')
    firefoxOptions.add_argument('--no-sandbox')
    firefoxOptions.add_argument('--disable-dev-shm-usage')
    firefoxOptions.add_argument('--blink-settings=imagesEnabled=false')
    firefoxOptions.add_argument('--disable-infobars')
    firefoxOptions.add_argument('--disable-browser-side-navigation')
    firefoxOptions.add_argument('--disable-features=VizDisplayCompositor')
    firefoxOptions.add_argument('--disable-gpu')
    firefoxOptions.add_argument('--force-device-scale-factor=1')
    firefoxOptions.add_argument('--disable-backgrounding-occluded-windows')
    firefoxOptions.add_argument('--disable-extensions')
    firefoxOptions.add_argument('--start-maximized')
    firefoxOptions.add_argument('--ignore-certificate-errors')
    #firefoxOptions.add_argument('--remote-debugging-port=' + self.port)
    firefoxOptions.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')   
    firefoxOptions.add_argument('--window-size=1280,1024')    
    firefoxOptions.add_argument('--user-data-dir=/home/licensesearch/chrome_data/' + self.port)
    firefoxOptions.add_argument('--allow-running-insecure-content')
    firefoxOptions.add_argument('--incognito') 
    

 
    service = ['--verbose']
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", self.proxy.split(':')[0])
    profile.set_preference("network.proxy.http_port", self.proxy.split(':')[1])
    profile.update_preferences()

    options = {
        'proxy': {
            'http': 'http://' + self.proxy,
            'https': 'https://' + self.proxy,
           # 'no_proxy': 'localhost,127.0.0.1'
        },
      # 'port': 30000 + int(index)
    }

    self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), firefox_profile=profile, seleniumwire_options=options, options=firefoxOptions)

    print('finished creating driver')
    # self.driver.set_script_timeout(10) #Both settings are effective
    # self.driver.set_page_load_timeout(10)
   # print(self.driver.seleniumwire_options['proxy'])
    print('Created browser: ', self.port, self.proxy)

  def ResetCookie(self):
    if self.driver:
      self.driver.delete_all_cookies()
      time.sleep(1)

  def close(self):
    if self.driver:
      self.driver.quit()
      self.driver = None
    
    # kill all chrome processes w/ assigned debug port
    for retries in range(0, 5):
      try:
        for process in psutil.process_iter():
          if process.name() == 'chrome' and '--remote-debugging-port=' + self.port in process.cmdline():
            
            print('Terminating: ', process.pid, '--remote-debugging-port=' + self.port)
            if retries > 1:
              process.kill()
            else:
              process.terminate()
            if retries > 0:
              process.wait(5)
      except Exception as err:
        continue
  
  def printStatus(self, message, param1 = '', param2 = ''):
    print('ChromeWebDriver[' + str(self.index) +']:', message, param1, param2)

  def reinitialize(self):
    self.printStatus('reinitializing...')
    self.initialize()

  def handleException(self, method, exception):
    self.stats['exception'] += 1
    self.printStatus('[' + type(exception).__name__ +':' + method +']: ', exception, self.saveScreenshot(method + '.exception', True))
    traceback.print_exc()
  
  def requestUrl(self, url, condition = None, timeout = 300):
    self.stats['request_url'] += 1
    for retries in range(0, 4):
      if not self.driver or retries > 1:
        self.initialize()
      try:
        self.driver.get(url)
        if condition:
          return self.waitUntil(condition, timeout)
        else:
          return True
      except Exception as error:
        self.handleException('requestUrl', error)
  
  def waitUntil(self, condition, timeout = 300):
    try:
      return WebDriverWait(self.driver, timeout).until(condition)
    except Exception as error:
      print ("waitUntil Timeout")
      #print(error)
      # self.handleException('waitUntil', error)
    return None

  # From: http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
  # Click element and wait for condition (by default: wait for URL to change)
  def clickElement(self, startCondition, endCondition = None, allowUrlRefresh = True, expectNewUrl = True, timeout = 300):
    self.stats['click_element'] += 1
    oldUrl = None
    for retries in (range(0, 5) if allowUrlRefresh else range (0, 1)):
      try:
        if not oldUrl:
          oldUrl = self.driver.current_url # record original URL before click
        if oldUrl:
          if retries > 0 and allowUrlRefresh:
            self.requestUrl(oldUrl)
          element = self.waitUntil(startCondition)
          if element:
            print(self.index, ': clicking...')
            element.click()
            print(self.index, ': clicked')
            if expectNewUrl: # default: URL changes after click
              print(self.index, ': waiting for url change: ', oldUrl)
              self.waitUntil(EC.url_changes(oldUrl), timeout)
              print(self.index, ': new url', self.driver.current_url)
            if endCondition:
              print(self.index, ': waiting for end condition')
              return self.waitUntil(endCondition, timeout)
            return True
      except Exception as error:
        self.handleException('clickElement', error)
    return False

  def getElementAttribute(self, element, attribute):
    try:
      return element.get_attribute(attribute)
    except Exception as error:
      self.handleException('getElementAttribute', error)
      return ''

  def getElementText(self, element):
    try:
      return element.text
    except Exception as error:
      self.handleException('getElementAttribute', error)
      return ''
  
  def clickElementByXPath(self, xpath):
    try:
      element = self.driver.find_element(By.XPATH, xpath)
      return element.click()
    except Exception as error:
      self.handleException('clickElement', error)
      return ''
      


  def typeCharacterByXPath(self, xpath, text):
    try:
      element = self.driver.find_element(By.XPATH, xpath)
      for ch in text:
          element.send_keys(ch)
          time.sleep(0.15)
      return True
    except Exception as error:
      self.handleException('typeText', error)
      return ''

  def typeTextByXPath(self, xpath, text):
    try:
      element = self.driver.find_element(By.XPATH, xpath)
      return element.send_keys(text)
    except Exception as error:
      self.handleException('typeText', error)
      return ''

  def clearTextByXPath(self, xpath):
    try:
      element = self.driver.find_element(By.XPATH, xpath)
      return element.clear()
    except Exception as error:
      self.handleException('clearText', error)
      return ''

  def execute_script(self, script):
    try:
        self.driver.execute_script(script)
    except Exception as error:
      self.handleException('execute_script', error)
      return '' 
  
  def getElementByXPath(self, xpath):
    try:
        element = self.driver.find_element(By.XPATH, xpath)
        return element
    except Exception as error:
      self.handleException('getElement', error)
      return ''

  def getCurrentUrl(self):
    try:
      return self.driver.current_url
    except Exception as error:
      self.handleException('getCurrentUrl', error)
      return ''

  def getElementsByXPath(self, xpath):
    try:
        elements = self.driver.find_elements(By.XPATH, xpath)
        return elements
    except Exception as error:
      self.handleException('getElements', error)
      return ''  

  def getCurrentPage(self):
    return self.driver.title.strip() + ' [' + self.driver.current_url + ']'

  def saveScreenshot(self, filename, unique = False):
    screenshotPath = self.paths['screenshots']
    if unique:
      screenshotPath += 'S' + str(self.screenshotCount) + '_'
      self.screenshotCount += 1
    screenshotPath += filename + '.png'
    print (screenshotPath)
    try:
      self.driver.get_screenshot_as_file(screenshotPath)
      return screenshotPath
    except Exception as error:
      return '[error: ' + str(error) + ']';
      
  def getTitle(self):
    try:
      return self.driver.title
    except Exception as error:
      self.handleException('getTitle', error)
      return '';

  def getDriver(self):
    return self.driver
  
  def getStatsSummary(self):
    return str(self.stats['exception']) + '/' + str(self.stats['request_url'] + self.stats['click_element'])

  def getXhrReponse(self, xhrSearchPath):
    out = None
    for request in self.driver.requests:
      if request.response:
        if xhrSearchPath in request.url:
          out = decompress(request.response.body)
    return out

  def getXhrVin(self):
    out = None
    for request in self.driver.requests:
      if request.response:
        try:
          if('/smc/smb/vins' in request.url):
            retval = request.response.body.decode("utf-8")
            retObj = json.loads(retval)
            print(retObj)
            if('status' in retObj):
              if(retObj['status'] == 'Bad recaptcha token'):
                 return "recaptcha"

            if('vinInfos' in retObj):
              for key, value in retObj['vinInfos'].items():
                if(len(key) > 0):
                  return key

            print(retObj)
        except Exception as ex:
          print(request.response.body)
          print(ex)
    return out
  def process_browser_logs_for_network_events(self):
    logs = self.driver.get_log("performance")
    """
    Return only logs which have a method that start with "Network.response", "Network.request", or "Network.webSocket"
    since we're interested in the network events specifically.
    """
    for entry in logs:
      log = json.loads(entry["message"])["message"]
      if (
              "Network.response" in log["method"]
              or "Network.request" in log["method"]
              or "Network.webSocket" in log["method"]
      ):
        yield log

