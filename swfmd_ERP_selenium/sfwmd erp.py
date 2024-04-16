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
        permit_type_select = wait.until(EC.presence_of_element_located((By.NAME, "permitFamilyType")))
        Select(permit_type_select).select_by_visible_text('ERP')
        time.sleep(5)
        # Select From Date (January 1, 2024)
        day_from_select = wait.until(EC.presence_of_element_located((By.NAME, "fromdateDate")))
        Select(day_from_select).select_by_value('01')

        month_from_select = wait.until(EC.presence_of_element_located((By.NAME, "fromdateMonth")))
        Select(month_from_select).select_by_visible_text('JAN')

        year_from_select = wait.until(EC.presence_of_element_located((By.NAME, "fromdateYear")))
        Select(year_from_select).select_by_visible_text('2024')
        time.sleep(5)

        # Select To Date (April 15, 2024)
        day_to_select = wait.until(EC.presence_of_element_located((By.NAME, "todateDate")))
        Select(day_to_select).select_by_visible_text('15')

        month_to_select = wait.until(EC.presence_of_element_located((By.NAME, "todateMonth")))
        Select(month_to_select).select_by_visible_text('APR')

        year_to_select = wait.until(EC.presence_of_element_located((By.NAME, "todateYear")))
        Select(year_to_select).select_by_visible_text('2024')
        time.sleep(5)

        # Click the Search button
        search_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"][value="Search Records"]')))
        search_button.click()
        print("Search clicked")
        time.sleep(10)  # Allow time for the search results to load

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
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()
        print("Driver closed.")

if __name__ == "__main__":
    crawl_information()
