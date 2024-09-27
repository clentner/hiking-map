import undetected_chromedriver as webdriver
import time

# set up selenium driver to show the browser window (i.e., non-headless mode)
driver = webdriver.Chrome()

# navigate to the login page
driver.get('https://www.alltrails.com/')

# pause the script and wait for user to log in manually
input("Log in manually, then press Enter to continue...")

# now selenium can take over to automate the rest of the process
driver.get('https://www.alltrails.com/users/your_username/recordings')

# proceed with your automation here...
time.sleep(5)  # let the page load, etc.

