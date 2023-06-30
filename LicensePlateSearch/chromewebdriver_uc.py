# http://vautoextract.vindb.org//licenseapi.php?key=24GCRN4UT2TIZIS&plate=TT42Q23&state=GA
# http://docs.autoscale.ventures/pages/viewpage.action?pageId=35127548&fbclid=IwAR3_dEul46F7PRbZ24-9ts9kgVmvim4YgTd2MgwH1qAp5mIEOE845Olxds0
import selenium
import time
import os
import shutil
import psutil
import traceback
import json
#import undetected_chromedriver as uc
import seleniumwire.undetected_chromedriver as uc

import seleniumwire
from seleniumwire import webdriver
from gzip import decompress

from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



class ChromeWebDriver:

  DRIVER_PATH = '/home/rahul/Desktop/lp2/licensesearch/chromedrivers/v92/chromedriver'
  DEBUG_PATH = '/home/rahul/Desktop/lp2/licensesearch/webdriver_debug/'
  
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
    capabilities = webdriver.DesiredCapabilities.CHROME
    #capabilities['loggingPrefs'] = {'performance': 'ALL'}
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

    #capabilities['proxy'] = {
    #  'httpProxy': self.proxy,
    #  'ftpProxy': self.proxy,
    #  'sslProxy': self.proxy,
    #  'proxyType': 'MANUAL',
    #}
    self.close() # kill previous instances
    #chromeOptions = webdriver.ChromeOptions()
    chromeOptions = uc.ChromeOptions()
    #chromeOptions.add_argument('--headless')
    #chromeOptions.add_argument('--no-sandbox')
    chromeOptions.add_argument('--disable-dev-shm-usage')

    chromeOptions.add_argument('--blink-settings=imagesEnabled=false')
    chromeOptions.add_argument('--disable-infobars')
    chromeOptions.add_argument('--disable-browser-side-navigation')
    chromeOptions.add_argument('--disable-features=VizDisplayCompositor')
    chromeOptions.add_argument('--disable-gpu')
    chromeOptions.add_argument('--force-device-scale-factor=1')
    chromeOptions.add_argument('--disable-backgrounding-occluded-windows')
    chromeOptions.add_argument('--disable-extensions')
    chromeOptions.add_argument('--start-maximized')
    chromeOptions.add_argument('--ignore-certificate-errors')
    chromeOptions.add_argument('--remote-debugging-port=' + self.port)
    chromeOptions.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')   
    chromeOptions.add_argument('--window-size=1280,1024')    
    chromeOptions.add_argument('--user-data-dir=/home/rahul/Desktop/lp2/licensesearch/chrome_data/' + self.port)
    chromeOptions.add_argument('--allow-running-insecure-content')
    chromeOptions.add_argument('--incognito')
    chromeOptions.add_argument('--proxy-server='+ proxy)
    chromeOptions.set_capability(
      "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL","network": "ALL"}
    )
    #chromeOptions.add_experimental_option('w3c', False)

    #chromeOptions.add_argument('--proxy-server=%s' % proxy)
    print('creating driver')
    options = {
        'proxy': {
            'http': 'http://' + self.proxy,
            'https': 'https://' + self.proxy,
            'no_proxy': 'localhost,127.0.0.1'
        },
      # 'port': 30000 + int(index)
    }

    chromeOptions = {
        'proxy': {
            'http': 'http://' + self.proxy,
            'https': 'https://' + self.proxy,
           # 'no_proxy': 'localhost,127.0.0.1'
        },
      # 'port': 30000 + int(index)
    }
    print ('Test Selenium Options', options)
    #self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),chrome_options=chromeOptions,seleniumwire_options=options,desired_capabilities=capabilities)
    self.driver = uc.Chrome(version_main=113, chrome_options=chromeOptions,seleniumwire_options=options,desired_capabilities=capabilities)
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

  def getSource(self):
    try:
      return self.driver.page_source
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

  def getCurrentUrl(self):
    return self.driver.current_url

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

  def getXhrReponse4(self):
    out = None
    for request in self.driver.requests:
      try:
        print(request.response.body)
        print(decompress(request.response.body))
      except Exception as ex:
        print(request.response.body)
        print(ex)
        continue
    return out

  def getXhrReponse3(self):
    for request in self.driver.requests:
      try:
        if request.response:
          print(
          request.url,
          request.response.status_code,
          request.headers,
          request.response.headers
          )
      except Exception as ex:
        print(ex)

  def getXhrReponse2(self):
    out = None
    for request in self.driver.requests:

      print(request.response.body)
      try:
        out = decompress(request.response.body)
        print(out)
        print(self.driver.get_log('browser'))
        print(self.driver.get_log('driver'))
        print(self.driver.get_log('client'))
        print(self.driver.get_log('server'))
      except Exception as ex:
        print(ex)
      #print(out)


  def process_browser_log_entry(self):
      response = json.loads(entry['message'])['message']
      return response

  def getXhrReponse4(self):
    browser_log = self.driver.get_log('vin')
    events = [self.process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.response' in event['method']]
    print(events)

  def process_browser_logs_for_network_events(self):
    logs = self.driver.get_log("performance")
    """
    Return only logs which have a method that start with "Network.response", "Network.request", or "Network.webSocket"
    since we're interested in the network events specifically.
    """
    for entry in logs:
      try:
        log = json.loads(entry["message"])["message"]
      except Exception as ex:
        print(ex)
        continue
      yield log

  def getVinFromRaw(self):
    ##visit your website, login, etc. then:
    logs_raw = self.driver.get_log("network")
    self.driver.get_log
    #print("performace log is :" + logs_raw)
    logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
    #json.loads(str(logs_raw))
    #print(logs_raw['postData'])
    file1 = open(r"C:\Users\admin\Downloads\myfile3.txt", "w")
    file1.writelines(json.dumps(logs_raw))
    file1.close()


    def log_filter(log_):
      return (
        # is an actual response
              log_["method"] == "Network.responseReceived"
              # and json
              and "json" in log_["params"]["response"]["mimeType"]
      )

    for log in filter(log_filter, logs):
      try:
        #print(log)
        request_id = log["params"]["requestId"]
        resp_url = log["params"]["response"]["url"]
        #print(f"Caught {resp_url}")
        #print(request_id)
        retVal = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
        if('body' in retVal and len(retVal['body']) > 0 and 'vin' in retVal['body'][0]):
          return retVal['body']
      except Exception as ex:
        print("ERRRORRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
        print(ex)
    return None
