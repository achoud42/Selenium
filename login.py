import  undetected_chromedriver   as uc
#import Chrome
from time                          import sleep
from selenium.webdriver.common.by  import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support    import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys



class Google:
    def __init__(self) -> None:
        self.url    = 'https://accounts.google.com/ServiceLogin'
        options = uc.ChromeOptions()
        options.add_argument("--disable-popup-blocking")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-gpu')
    
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-gpu')
        options.add_argument('--force-device-scale-factor=1')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-extensions')
        options.add_argument('--start-maximized')
        options.add_argument('--ignore-certificate-errors')
        #options.add_argument('--remote-debugging-port=' + self.port)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')   
        options.add_argument('--window-size=1280,1024')    
        #options.add_argument('--user-data-dir=/home/rahul/Desktop/lp2/licensesearch/chrome_data/' + self.port)
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--incognito')
        #options.add_argument('--proxy-server='+ proxy)
        options.add_argument("--disable-popup-blocking")
        options.set_capability(
      "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL","network": "ALL"}
         )

        self.driver = uc.Chrome(options=options); self.driver.get(self.url)
        self.time   = 10
    
    def login(self, email, password, recovery_email):
        sleep(2)
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.NAME, 'identifier'))).send_keys(f'{email}\n')
        sleep(2)
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.NAME, 'Passwd'))).send_keys(f'{password}\n')
        sleep(5)
        recovery_emailXPath = "//*[@id='view_container']/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/ul/li[3]/div/div[2]"
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, recovery_emailXPath))).click()
        sleep(2)
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.NAME, 'knowledgePreregisteredEmailResponse'))).send_keys(f'{recovery_email}\n')
        sleep(5)
        self.driver.close()
        #self.code()

    def code(self):
    # [ ---------- paste your code here ---------- ]
        #action = ActionChains(self.driver)
        #action.key_down(Keys.COMMAND).send_keys('t').key_up(Keys.COMMAND).perform()
        site = "https://www.google.com"
        self.driver.execute_script(f'''window.open("{site}","_blank");''')

        self.driver.switch_to.window(self.driver.window_handles[-1])

        sleep(3)
        self.driver.get(self.url)
        sleep(self.time)                                                                                  

if __name__ == "__main__":
    #  ---------- EDIT ----------
    email = 'satishsingh801304@gmail.com' # replace email
    password = 'K4nB2$8fg3eS170' # replace password
    recovery_email = 'pinkidevidharmaychak@gmail.com'
    #  ---------- EDIT ----------                                                                                                                                                         
    
    google = Google()
    google.code()
    #google.login(email, password,recovery_email)