from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class LinkedInJobScrapper:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless") # avoids opening a window to control the browser
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # prevents chrome from flagging itself as being under automation
        chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])  # makes browser ui & behavior harder to detect that it is a bot
        chrome_options.add_experimental_option("useAutomationExtension", False)  # reduces automation fingerprints
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")  # makes the bot look like a real user

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(1920, 1080)

        # This command is used to become avoid being detected by the website.
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def open_url(self, url):
        self.driver.get(url)

    def close_signin_popup(self):
        self.driver.execute_script("""
        // Remove the modal popup
        const modal = document.querySelector('button.cta-modal__dismiss-btn')?.closest('div[class*="modal"]');
        if (modal) {
            modal.remove();
        }

        // Remove the overlay blocking clicks
        const overlay = document.querySelector('.modal__overlay');
        if (overlay) {
            overlay.remove();
        }""")
        self.driver.execute_script("""
        // Restore body scroll
        document.body.style.overflow = 'auto';
        document.documentElement.style.overflow = 'auto';""")

    def quit(self):
        self.driver.quit()