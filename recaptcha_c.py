from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import logging
import os
from chromewebdriver_uc import ChromeWebDriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from time import *
import test_ips
import json
ip_list = list(test_ips.TEST_IPS)
state_file = '/root/state.txt'


PROCESS_NUMBER = 9
scores ={}
n = 0
#proxy ='38.170.111.196:8800'

if os.path.isfile(state_file):
    with open(state_file, 'r') as f:
      n = int(f.read().strip())
else:
      n = 1

for item in ip_list[n-1:]:
   proxy = item.replace('"', '')
   print(proxy)
   #proxy ='38.170.111.196:8800'
   #n = n+1
   scoreXPath = '//*[@id="score"]'
   chromeWebDriver = ChromeWebDriver(PROCESS_NUMBER, proxy, 9)
   chromeWebDriver.requestUrl('https://ip-check.net/recaptchav3?format=text')
   sleep(5)

   score = chromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, scoreXPath)), 10)
   #print(score)
   result = chromeWebDriver.getElementByXPath(scoreXPath).text
   result = result.split(':')
   print(result)
   result = (result[1].strip())
   print(result)
   scores['ip']=proxy
   scores['score']=result
   scores['count']=n
   if result <= '0.3' :
      with open("/root/output3.txt", "r") as f:
          existing_lines = f.readlines()

      with open("/root/output3.txt", "w") as f:
          for line in existing_lines:
              f.write(line)

          f.write(json.dumps(scores) + "\n")
          #f.close()
          print("Done writing to file.")

   else :
      with open("/root/good_ips.txt", "r") as f:
          existing_lines = f.readlines()

      with open("/root/good_ips.txt", "w") as f:
          for line in existing_lines:
              f.write(line)

          f.write(json.dumps(scores) + "\n")
          #f.close()
          print("Done writing to file.")
   n= n+1
   with open(state_file, 'w') as f:
        f.write(str(n))
   chromeWebDriver.ResetCookie()
   print("reset the cookies   now closing the browser")
   sleep(1)
   chromeWebDriver.close()
