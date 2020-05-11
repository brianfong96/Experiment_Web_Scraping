from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def CreateDriver(extra_arguments = ["--start-maximized"]):
    arguments = ['--ignore-certificate-errors', '--incognito', '--headless']
    arguments += extra_arguments
    #Use selenium and open webdriver
    options = webdriver.ChromeOptions()
    for arg in arguments:
        options.add_argument(arg)    

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

def SetupDriver():
    driver = CreateDriver()
    if driver:
        driver.quit()
    return

if __name__ == "__main__":
    driver = CreateDriver()
    
    pass