from selenium import webdriver
from selenium.webdriver import ActionChains
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
        # Select From Date (January 1, 2024)
        day_from_select = wait.until(EC.presence_of_element_located((By.NAME, "fromdateDate")))
        Select(day_from_select).select_by_value('01')

        month_from_select = wait.until(EC.presence_of_element_located((By.NAME, "fromdateMonth")))
        Select(month_from_select).select_by_visible_text('JAN')

        year_from_select = wait.until(EC.presence_of_element_located((By.NAME, "fromdateYear")))
        Select(year_from_select).select_by_visible_text('2024')

        # Select To Date (April 15, 2024)
        day_to_select = wait.until(EC.presence_of_element_located((By.NAME, "todateDate")))
        Select(day_to_select).select_by_visible_text('15')

        month_to_select = wait.until(EC.presence_of_element_located((By.NAME, "todateMonth")))
        Select(month_to_select).select_by_visible_text('APR')

        year_to_select = wait.until(EC.presence_of_element_located((By.NAME, "todateYear")))
        Select(year_to_select).select_by_visible_text('2024')

        # Click the Search button
        search_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"][value="Search Records"]')))
        search_button.click()
        print("Search clicked")
        time.sleep(5)  # Allow time for the search results to load

        # Continuously process until no more pages are available
        while True:
            # Find and process each application link
            applications = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "a[href*='DetailedReport']")))

            # Filter out any applications where the 'href' attribute is null or empty
            filtered_applications = [app for app in applications if app.get_attribute('href') and app.is_displayed()]

            # Capture current window handle before the click
            main_window = driver.current_window_handle
            all_windows_before_click = driver.window_handles

            for app in applications:
                app.click()
                print(f"'{app.text}'")
                time.sleep(2)
                # Get new window handle and switch to it
                new_windows = [window for window in driver.window_handles if window not in all_windows_before_click]
                if new_windows:
                    driver.switch_to.window(new_windows[0])

                    # Now interact in the new window
                    calculation_element = driver.find_elements(By.XPATH, "//*[starts-with(normalize-space(text()), 'Calculations - Design Plans')]")
                    if (calculation_element):
                        print('element found')
                        ActionChains(driver).move_to_element(calculation_element[0]).click().perform()
                        maps_elements = driver.find_elements(By.XPATH, "//*[starts-with(normalize-space(text()), 'Maps')]")
                        if (maps_elements):
                            print('maps_element found')
                            ActionChains(driver).move_to_element(maps_elements[0]).click().perform()
                            time.sleep(2)
                        plans_elements = driver.find_elements(By.XPATH,
                                                              "//*[starts-with(normalize-space(text()), 'Plans')]")
                        if (plans_elements):
                            print('plans_elements found')
                            ActionChains(driver).move_to_element(plans_elements[0]).click().perform()
                            time.sleep(2)
                        # After clicking 'Maps and plans', find all <a> links that include 'docdownload' in their href attribute
                        doc_links = driver.find_elements(By.XPATH,
                                                         "//span[contains(@style, 'display: block;')]//a[contains(@href, 'docdownload')]")
                        print(f"Found {len(doc_links)} document download link(s).")

                        # Iterate through each found link and click
                        for link in doc_links:
                            print(f"Clicking on link: {link.get_attribute('href')}")
                            # Ensure each link is in the viewport and then click
                            driver.execute_script("arguments[0].scrollIntoView(true);", link)
                            time.sleep(0.5)  # Small pause to ensure scrolling has completed
                            link.click()  # Perform the click action
                            time.sleep(2)  # Wait 2 seconds after each click

                    # Close the new window and switch back to the original window
                    driver.close()
                    driver.switch_to.window(main_window)
                else:
                    print("No new window opened")
                time.sleep(1)  # Wait for folder contents to load

                # Check for and click the next page button if available
            try:
                next_page = driver.find_element_by_css_selector('a[href*="IterateReport.do?page=next"]')
                next_page.click()
                time.sleep(5)  # Wait for the next page of results to load
            except:
                print("No more pages to process.")
                break
    finally:
        driver.quit()
        print("Driver closed.")

if __name__ == "__main__":
    crawl_information()
