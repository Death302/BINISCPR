from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from selenium.common.exceptions import NoSuchElementException

# Create a log file to record errors
log_file = open('log.txt', 'w')

try:
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/brave-browser"  # Update this path
    # chrome_options.add_argument("--headless")  # Run in headless mode

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the login page
    driver.get("https://www.bniconnectglobal.com/login/")
    time.sleep(5)

    # Perform Login
    driver.find_element(By.NAME, 'username').send_keys("mrsoftwares")
    driver.find_element(By.NAME, 'password').send_keys("Rozroznewpass*00")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait for login to complete
    time.sleep(5)

    # Click to search people
    driver.find_element(By.CLASS_NAME, 'searchpeople').click()
    time.sleep(5)

    # Advanced Search and fill fields
    driver.find_element(By.ID, 'advancedSearch').click()
    driver.find_element(By.ID, 'memberKeywords').send_keys("Lawyer")
    Select(driver.find_element(By.ID, 'memberIdCountry')).select_by_visible_text('India')
    driver.find_element(By.ID, 'searchConnections').click()
    time.sleep(5)

    # Create and open CSV file
    with open('output.csv', 'w', newline='') as csvfile:
        fieldnames = set()  # Initialize an empty set to store unique fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()  # Write an empty header first. You can rewrite this later.

        main_window = driver.current_window_handle

        while True:
            table_body = driver.find_element(By.ID, 'tableBody')
            links = table_body.find_elements(By.XPATH, "//a[@target='_blank' and @class='link']")

            for link in links:
                link.click()
                new_window = [window for window in driver.window_handles if window != main_window][0]
                driver.switch_to.window(new_window)
                time.sleep(2)

                # Initialize row data
                row_data = {}

                # Locate and scrape the data
                labels_and_values = driver.find_elements(By.CSS_SELECTOR, 'label')
                for label in labels_and_values:
                    try:
                        text_element = label.find_element(By.CSS_SELECTOR, 'span.text')
                        field_element = label.find_element(By.CSS_SELECTOR, 'span.fieldtext')
                        row_data[text_element.text] = field_element.text
                        fieldnames.add(text_element.text)  # Dynamically update fieldnames
                    except NoSuchElementException:
                        print("Some elements are missing. Skipping...")
                        continue
                
                writer = csv.DictWriter(csvfile, fieldnames=list(fieldnames))
                writer.writerow(row_data)  # Write the scraped data to CSV
                
                driver.close()
                driver.switch_to.window(main_window)
                time.sleep(2)
            
            # Check for the presence of a "Next" button and scroll to it if it exists
            try:
                next_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'datalist_next')))
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                next_button.click()
                time.sleep(5)  # You can adjust the sleep time as needed
            except NoSuchElementException:
                error_message = "No more 'Next' button. Exiting..."
                print(error_message)
                log_file.write(error_message + '\n')
                break  # Exit the loop if the "Next" button is not found
            except Exception as e:
                error_message = f"An error occurred: {e}"
                print(error_message)
                log_file.write(error_message + '\n')

except NoSuchElementException as e:
    error_message = f"Element not found: {e}"
    print(error_message)
    log_file.write(error_message + '\n')
    driver.quit()
except Exception as e:
    error_message = f"An unexpected error occurred: {e}"
    print(error_message)
    log_file.write(error_message + '\n')
    driver.quit()

# Close the log file
log_file.close()
