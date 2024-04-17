from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import shutil


def ensure_folder_exists(folder_path):
    """Ensure the folder exists, and create it if it does not."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    print(f"Folder created: {folder_path}")

def move_files_to_folder(download_path, folder_name):
    """Move all files from the download directory to a specified folder named after the application."""
    folder_path = os.path.join(download_path, folder_name)
    ensure_folder_exists(folder_path)

    # Move all files in the download directory to the new folder
    for file in os.listdir(download_path):
        file_path = os.path.join(download_path, file)
        # Ensure the item is a file before attempting to move it
        if os.path.isfile(file_path):
            shutil.move(file_path, os.path.join(folder_path, file))
    print(f"All files moved to {folder_path}")
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def ensure_element_ready(driver, xpath, timeout=15):
    """ Wait until the element is visible and has a size. """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        # Additional check to make sure the element has height and width
        return element if element.size['width'] > 0 and element.size['height'] > 0 else None
    except TimeoutException:
        print(f"Timeout waiting for the element: {xpath}")
        return None
def wait_for_file_download_completion(folder_path, timeout=600):
    """Wait for all .crdownload files in the specified folder to disappear."""
    start_time = time.time()
    while True:
        if all(not filename.endswith('.crdownload') for filename in os.listdir(folder_path)):
            print("All files have finished downloading.")
            break
        elif (time.time() - start_time) > timeout:
            print("Timeout reached while waiting for downloads to complete.")
            break
        time.sleep(1)  # Check every second
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
            time.sleep(2)

            # Initialize a set to keep track of clicked links
            clicked_links = set()

            # Find and process each application link
            applications = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "a[href*='DetailedReport']")))

            # Filter out any applications where the 'href' attribute is null or empty
            filtered_applications = [app for app in applications if app.get_attribute('href') and app.is_displayed()]

            # Capture current window handle before the click
            main_window = driver.current_window_handle
            all_windows_before_click = driver.window_handles

            for app in filtered_applications:
                driver.execute_script("arguments[0].scrollIntoView(true);", app)
                app_text = app.text
                if app_text not in clicked_links:
                    app.click()
                    print(f"'Handling Application# {app_text}'")
                    clicked_links.add(app_text)
                    time.sleep(2)
                    # Get new window handle and switch to it
                    new_windows = [window for window in driver.window_handles if window not in all_windows_before_click]
                    if new_windows:
                        driver.switch_to.window(new_windows[0])

                        # Now interact in the new window
                        calculation_element = driver.find_elements(By.XPATH,
                                                                   "//*[starts-with(normalize-space(text()), 'Calculations - Design Plans')]")
                        if not calculation_element or not calculation_element[0].is_displayed():
                            print("No calculation element found, or it is not visible. Skipping to next application.")
                            driver.close()  # Close the current window
                            driver.switch_to.window(main_window)  # Switch back to the main window
                            continue  # Skip to the next application

                        if calculation_element:
                            ActionChains(driver).move_to_element(calculation_element[0]).click().perform()
                            maps_elements = driver.find_elements(By.XPATH,
                                                                 "//*[starts-with(normalize-space(text()), 'Maps')]")
                            if maps_elements:
                                ActionChains(driver).move_to_element(maps_elements[0]).click().perform()
                                time.sleep(2)
                            plans_elements = driver.find_elements(By.XPATH,
                                                                  "//*[starts-with(normalize-space(text()), 'Plans')]")
                            if plans_elements:
                                ActionChains(driver).move_to_element(plans_elements[0]).click().perform()
                                time.sleep(2)

                            sealed_elements = driver.find_elements(By.XPATH,
                                                                   "//*[starts-with(normalize-space(text()), 'Sealed Document Authentication')]")
                            if sealed_elements:
                                ActionChains(driver).move_to_element(sealed_elements[0]).click().perform()
                                time.sleep(2)
                            # After clicking 'Maps and plans', find all <a> links that include 'docdownload' in their href attribute
                            doc_links = driver.find_elements(By.XPATH,
                                                             "//span[contains(@style, 'display: block;')]//a[contains(@href, 'docdownload')]")
                            print(f"Found {len(doc_links)} document download link(s).")

                            # Iterate through each found link and click
                            for link in doc_links:
                                driver.execute_script("arguments[0].scrollIntoView(true);", link)
                                time.sleep(0.5)  # Small pause to ensure scrolling has completed
                                current_handles = driver.current_window_handle  # Existing window handles before click
                                link.click()  # Perform the click action
                                time.sleep(1)
                                driver.switch_to.window(current_handles)
                                time.sleep(5)  # Wait 5 seconds after each click

                        time.sleep(15)
                        # Move downloaded files to a new folder named after the application
                        move_files_to_folder(download_path, app_text)  # This is where you call the folder management
                        # Close the new window and switch back to the original window
                        driver.close()
                        driver.switch_to.window(main_window)
                    else:
                        print("No new window opened")
                time.sleep(1)  # Wait for folder contents to load
            try:
                print("clicking next page")
                next_page = driver.find_element(By.CSS_SELECTOR,
                                               "a[href*='IterateReport.do?page=next'] img[src*='nextcal.gif']")
                next_page.click()
                time.sleep(20)  # Wait for the next page of results to load
            except:
                print("No more pages to process.")
                break
    finally:
        driver.quit()
        print("Driver closed.")

if __name__ == "__main__":
    crawl_information()
