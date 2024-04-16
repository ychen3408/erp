from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


def crawl_information():
    download_path = r"C:\Users\lily\Downloads"
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,  # To auto download without asking
    })
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        # Navigate to the website
        driver.get("https://my.sfwmd.gov/ePermitting/PopulateLOVs.do?flag=1")

        # Select Permit Type (ERP)
        permit_type_select = driver.find_element_by_xpath('/html/body/table/tbody/tr[3]/td/table/tbody/tr[1]/td[2]/form/table/tbody/tr[4]/td[3]/select')
        Select(permit_type_select).select_by_visible_text('ERP')

        # Select From Date (January 1, 2024)
        day_from_select = driver.find_element_by_xpath('/html/body/table/tbody/tr[3]/td/table/tbody/tr[1]/td[2]/form/table/tbody/tr[16]/td[3]/select[1]')
        Select(day_from_select).select_by_visible_text('01')
        month_from_select = driver.find_element_by_xpath('/html/body/table/tbody/tr[3]/td/table/tbody/tr[1]/td[2]/form/table/tbody/tr[16]/td[3]/select[2]')
        Select(month_from_select).select_by_visible_text('01')
        year_from_select = driver.find_element_by_xpath('/html/body/table/tbody/tr[3]/td/table/tbody/tr[1]/td[2]/form/table/tbody/tr[16]/td[3]/select[3]')
        Select(year_from_select).select_by_visible_text('2024')

        # Select To Date (April 15, 2024)
        day_to_select = driver.find_element_by_xpath('/html/body/table/tbody/tr[3]/td/table/tbody/tr[1]/td[2]/form/table/tbody/tr[17]/td[3]/select[1]')
        Select(day_to_select).select_by_visible_text('15')
        month_to_select = driver.find_element_by_xpath('/html/body/table/tbody/tr[3]/td/table/tbody/tr[1]/td[2]/form/table/tbody/tr[17]/td[3]/select[2]')
        Select(month_to_select).select_by_visible_text('04')
        year_to_select = driver.find_element_by_xpath('/html/body/table/tbody/tr[3]/td/table/tbody/tr[1]/td[2]/form/table/tbody/tr[17]/td[3]/select[3]')
        Select(year_to_select).select_by_visible_text('2024')

        # Click the Search button
        search_button = driver.find_element_by_xpath('/html/body/table/tbody/tr[3]/td/table/tbody/tr[1]/td[2]/form/table/tbody/tr[19]/td/input[1]')
        search_button.click()
        time.sleep(5)  # Allow time for the search results to load

        # Continuously process until no more pages are available
        while True:
            # Find and process each application link
            applications = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//a[contains(@href, "linkThatDifferentiatesApplicationLinks")]')))
            for app in applications:
                app.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//a[text()="Calculations - Design Plans"]'))).click()
                time.sleep(1)  # Wait for folder contents to load

                files = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href, "downloadLinkIdentifier")]')))
                for file in files:
                    file.click()
                    time.sleep(1)  # Allow time for download to initiate

                close_button = driver.find_element_by_xpath(
                    '/html/body/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table[5]/tbody/tr[3]/td/input')
                close_button.click()
                time.sleep(1)  # Wait for the main page to reload

                # Check for and click the next page button if available
            try:
                next_page = driver.find_element_by_xpath(
                    '/html/body/table/tbody/tr[3]/td/table/tbody/tr[1]/td/table[4]/tbody/tr[22]/td/table/tbody/tr/td[2]/a')
                next_page.click()
                time.sleep(5)  # Wait for the next page of results to load
            except:
                print("No more pages to process.")
                break  # Exit the loop if no next page button is found

    driver.quit()

# Call the function from the main block
    if __name__ == "__main__":
        crawl_information()