from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver=webdriver.Chrome(options=options)

username= "test"
password= "test."
url="https://www.stealmylogin.com/demo.html"

driver.get(url)
sleep(2)
print('1')
username_field=driver.find_element(By.NAME, "username").send_keys(username)
sleep(2)
print('2')

password_field=driver.find_element(By.NAME, "password").send_keys(password)
sleep(2)
print('3')

login_button=driver.find_element(By.XPATH, '/html/body/form/input[3]')
login_button.click()
sleep(5)
print('4')
