from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import chromedriver_autoinstaller
import time
from datetime import datetime
import pytz  # For timezone handling
from selenium.common.exceptions import StaleElementReferenceException


# Chrome setup
chromedriver_autoinstaller.install()
driver = webdriver.Chrome()

# URLs
login_url = "https://spark-cloud.tibaparking.net/"
validation_url = "https://spark-cloud.tibaparking.net/miamicentralretail/validation/remote-validation/validate-ticket"

# Login function
def login():
    try:
        print("Logging in...")
        driver.get(login_url)

        # Click the login button
        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']/.."))
        )
        login_button.click()

        # Enter email
        email_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'mat-input-0'))
        )
        email_input.clear()
        email_input.send_keys("")#place log in email here.

        time.sleep(1)

        # Enter password
        password_input = driver.find_element(By.ID, 'mat-input-1')
        password_input.clear()
        password_input.send_keys("")# place the log in password here.

        # Click the final "Login" button
        login_button_final = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Login']/.."))
        )
        login_button_final.click()

        # Wait for redirection to validation page
        WebDriverWait(driver, 20).until(
            EC.url_to_be(validation_url)
        )
        print("Login successful and redirected to validation page.")
    except TimeoutException:
        print("Login took too long or failed.")
        driver.quit()
        exit()
    except Exception as e:
        print(f"An error occurred during login: {e}")
        driver.quit()
        exit()

def safe_find_element(locator, retries=3):
    """
    Safely find an element, handling stale element reference errors by re-fetching.
    """
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except StaleElementReferenceException:
            print(f"Stale element detected. Retrying... (Attempt {attempt + 1}/{retries})")
    print("Failed to locate element after retries.")
    return None

def safe_find_and_click(locator, retries=3):
    """
    Safely find an element and click it, handling stale element reference errors.
    """
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
            print("Clicked element successfully.")
            return True
        except StaleElementReferenceException:
            print(f"Stale element detected. Retrying... (Attempt {attempt + 1}/{retries})")
    print("Failed to click element after retries.")
    return False

def safe_find_and_interact(locator, interaction, retries=3):
    """
    Safely find an element and perform an interaction on it, handling stale elements.
    """
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(locator)
            )
            interaction(element)  # Perform the given interaction (e.g., click, send_keys)
            return True
        except StaleElementReferenceException:
            print(f"Stale element detected. Retrying... (Attempt {attempt + 1}/{retries})")
        except TimeoutException:
            print(f"Element not found: {locator}. Retrying... (Attempt {attempt + 1}/{retries})")
    print(f"Failed to interact with element after {retries} retries: {locator}")
    return False
# Ticket validation function
def validate_tickets(start_ticket, end_ticket):
    try:
        est = pytz.timezone('US/Eastern')
        end_time = datetime.now(est).replace(hour=23, minute=0, second=0, microsecond=0)

        print(f"Starting validation from ticket {start_ticket} until {end_ticket} or 11 PM EST.")
        current_ticket = start_ticket
        last_valid_ticket = None
        consecutive_not_found = 0

        while current_ticket <= end_ticket:
            if datetime.now(est) >= end_time:
                print("Reached 11 PM EST. Stopping validation.")
                break

            try:
                print(f"Validating ticket {current_ticket}...")

                if driver.current_url != validation_url:
                    driver.get(validation_url)

                # Input ticket number
                ticket_input_locator = (By.XPATH, "//input[@data-placeholder='Search by Ticket # or Car Plate']")
                def enter_ticket_number(element):
                    element.clear()
                    element.send_keys(str(current_ticket))
                if not safe_find_and_interact(ticket_input_locator, enter_ticket_number):
                    current_ticket += 1
                    continue

                # Click the search button
                search_button_locator = (By.CLASS_NAME, "tb-icon-search")
                def click_search_button(element):
                    element.click()
                if not safe_find_and_interact(search_button_locator, click_search_button):
                    current_ticket += 1
                    continue

                print("Clicked search button.")

                # Select ticket
                search_result_locator = (By.CLASS_NAME, "parker-search-item-base")
                def click_search_result(element):
                    element.click()
                if not safe_find_and_interact(search_result_locator, click_search_result):
                    print(f"Ticket {current_ticket} not found or exited. Skipping.")
                    consecutive_not_found += 1

                    if consecutive_not_found >= 3:
                        print("3 consecutive 'not found or exited' tickets. Waiting 15 minutes and restarting from the last valid ticket.")
                        time.sleep(15 * 60)  # Wait 15 minutes
                        if last_valid_ticket is not None:
                            current_ticket = last_valid_ticket + 1
                        consecutive_not_found = 0
                    else:
                        current_ticket += 1
                    continue

                print(f"Selected ticket {current_ticket}.")
                consecutive_not_found = 0  # Reset the counter after a successful selection

                # Check elapsed time
                elapsed_time_locator = (By.XPATH, "//div[@class='search-item-value']/tb-time-elapsed-counter")
                try:
                    elapsed_time_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(elapsed_time_locator)
                    )
                    elapsed_time_text = elapsed_time_element.text
                    elapsed_seconds = parse_elapsed_time(elapsed_time_text)
                    if elapsed_seconds < 300:  # Less than 10 minutes
                        wait_time = (60 * 30) - elapsed_seconds
                        print(f"Waiting {wait_time // 60} minutes and {wait_time % 60} seconds to validate ticket {current_ticket}.")
                        time.sleep(wait_time)
                    else:
                        print(f"Elapsed time for ticket {current_ticket} is sufficient: {elapsed_seconds // 60} minutes.")
                except TimeoutException:
                    print("Could not retrieve elapsed time. Proceeding to validate.")

                time.sleep(10)
                # Validate ticket
                validate_button_locator = (By.XPATH, "//span[text()='Validate Ticket']/..")
                def click_validate_button(element):
                    time.sleep(1)
                    element.click()
                if not safe_find_and_interact(validate_button_locator, click_validate_button):
                    current_ticket += 1
                    continue

                print("Clicked 'Validate Ticket' button.")
                time.sleep(1)

                # Check for validation result
                try:
                    failure_message = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Validation - Failed')]"))
                    )
                    print(f"Validation failed for ticket {current_ticket}: {failure_message.text}")
                except TimeoutException:
                    print(f"Ticket {current_ticket} validated successfully. ✅")
                    last_valid_ticket = current_ticket  # Update the last valid ticket

                current_ticket += 1

            except StaleElementReferenceException:
                print(f"Stale element detected for ticket {current_ticket}. Retrying...")
                continue
            except TimeoutException:
                print(f"Timeout encountered for ticket {current_ticket}. Skipping to the next ticket.")
                current_ticket += 1
                continue
            except Exception as e:
                print(f"Unexpected error for ticket {current_ticket}: {e}. Retrying with next ticket.")
                current_ticket += 1
                continue

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Validation process completed.")


def parse_elapsed_time(time_text):
    """Parse elapsed time from HH:MM:SS format to seconds."""
    try:
        h, m, s = map(int, time_text.split(":"))
        return h * 3600 + m * 60 + s
    except ValueError:
        print(f"Invalid elapsed time format: {time_text}.")
        return -1
if __name__ == "__main__":
    try:
        # Log in to the system
        login()
        
        # Prompt the user for the starting ticket number
        ticket = input("Enter the starting ticket number: ")
        
        # Validate and convert input to an integer
        if ticket.isdigit():
            start_ticket = int(ticket)
            print(f"Starting validation from ticket {start_ticket}.")
            
            # Start ticket validation
            validate_tickets(start_ticket, 199999)
        else:
            print("Invalid ticket number. Please enter a valid number.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up by closing the browser
        driver.quit()