from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chrome_options = Options()

#chrome_options.add_argument("--headless") # avoids opening a window to control the browser

chrome_options.add_argument("--disable-blink-features=AutomationControlled") # prevents chrome from flagging itself as being under automation
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) # makes browser ui & behavior harder to detect that it is a bot
chrome_options.add_experimental_option("useAutomationExtension", False) # reduces automation fingerprints
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36") # makes the bot look like a real user

driver = webdriver.Chrome(options=chrome_options)

location = "Morocco"
job_title = "Data Engineer"

no_space_location = location.replace(" ", "%20")
no_space_job_title = job_title.replace(" ", "%20")

search_url = f"https://www.linkedin.com/jobs/search/?keywords={no_space_job_title}&location={no_space_location}"

if __name__ == '__main__':
    driver.set_window_size(1920, 1080)

    # This command is used to become avoid being detected by the website.
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.get(search_url) # Visit website

    time.sleep(2)

    # BEGIN CLOSING POP UP SIGN
    driver.execute_script("""
        // Remove the modal popup
        const modal = document.querySelector('button.cta-modal__dismiss-btn')?.closest('div[class*="modal"]');
        if (modal) {
            modal.remove();
        }

        // Remove the overlay blocking clicks
        const overlay = document.querySelector('.modal__overlay');
        if (overlay) {
            overlay.remove();
        }
    """)
    # END CLOSING POP UP SIGN

    # BEGIN RESUMING THE SCROLLING ON THE WEBSITE
    driver.execute_script("""
        // Restore body scroll
        document.body.style.overflow = 'auto';
        document.documentElement.style.overflow = 'auto';
    """)
    # END THE PROCESS

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    job_cards = driver.find_elements(By.CSS_SELECTOR, '.job-search-card')

    card = job_cards[0]
    job_url = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
    print(job_url)
    print(card)

    time.sleep(60)
    driver.quit()
