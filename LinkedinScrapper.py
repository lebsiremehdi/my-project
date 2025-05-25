import time
import re
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.devtools.v133.fetch import continue_request


def extract_job_card_info(card):
    def safe_text(selector):
        try:
            return card.find_element(By.CSS_SELECTOR, selector).text.strip()
        except NoSuchElementException:
            return "N/A"
    return {
        "Job Title": safe_text(".base-search-card__title"),
        "Company Name": safe_text(".base-search-card__subtitle"),
        "Location": safe_text(".job-search-card__location")
    }


class LinkedInJobScrapper(webdriver.Chrome):
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless") # avoids opening a window to control the browser
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # prevents chrome from flagging itself as being under automation
        chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])  # makes browser ui & behavior harder to detect that it is a bot
        chrome_options.add_experimental_option("useAutomationExtension", False)  # reduces automation fingerprints
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")  # makes the bot look like a real user

        super().__init__(options=chrome_options)
        self.set_window_size(1920, 1080)

        # This command is used to become avoid being detected by the website.
        self.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def close_signin_popup(self):
        self.execute_script("""
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
        self.execute_script("""
        // Restore body scroll
        document.body.style.overflow = 'auto';
        document.documentElement.style.overflow = 'auto';""")

    def open_url(self, url):
        self.get(url)

    def safe_scrolls(self, num_scrolls=5, time_lapse=1.5):
        for _ in range(num_scrolls):
            self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(time_lapse)

    def _get_work_type(self):
        try:
            items = self.find_elements(By.XPATH, "//li[contains(@class, 'job-insight')]")
            for item in items:
                txt = item.text.strip().lower()
                if "distance" in txt:
                    return "À distance"
                if "hybride" in txt:
                    return "Hybride"
                if "présentiel" in txt:
                    return "Présentiel"
            return "Inconnu"
        except NoSuchElementException:
            return "Inconnu"

    def _get_experience_level(self):
        try:
            desc = self.find_element(By.CSS_SELECTOR, ".show-more-less-html__markup").text
            if re.search(r"\binternship\b", desc, re.IGNORECASE):
                return "Internship"
            if re.search(r"\bentry level\b", desc, re.IGNORECASE):
                return "Entry level"
            match = re.search(r"(\d+)\+?\s*(ans|years)", desc, re.IGNORECASE)
            if match:
                return f"{match.group(1)}+ years"
        except NoSuchElementException:
            pass
        return "Unknown"

    def _get_education_level(self):
        try:
            desc = self.find_element(By.CSS_SELECTOR, ".show-more-less-html__markup").text
            if re.search(r"bac\s*\+\s*5", desc, re.IGNORECASE):
                return "Bac +5"
            elif re.search(r"bac\s*\+\s*3", desc, re.IGNORECASE):
                return "Bac +3"
            elif re.search(r"master|mastère", desc, re.IGNORECASE):
                return "Master"
            elif re.search(r"licence|bachelor", desc, re.IGNORECASE):
                return "Licence/Bachelor"
            elif re.search(r"doctorat|ph\.d", desc, re.IGNORECASE):
                return "Doctorat"
        except NoSuchElementException:
            pass
        return "Inconnu"

    def _get_offer_criteria(self):
        result = {}
        items = self.find_elements(By.XPATH, "//ul[@class='description__job-criteria-list']//li")
        for item in items:
            label = item.find_element(By.XPATH, "./h3").text.strip()
            value = item.find_element(By.XPATH, "./span").text.strip()
            result[label] = value
        return result

    def gather_card_info(self, card):
        try:
            result = {"job_url": card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")}

            for key, val in extract_job_card_info(card).items():
                result[key] = val

            self.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
            time.sleep(1.5)
            card.click()
            time.sleep(1.5)

            items = self.find_elements(By.XPATH, "//ul[@class='description__job-criteria-list']//li")
            for item in items:
                label = item.find_element(By.XPATH, "./h3").text.strip()
                value = item.find_element(By.XPATH, "./span").text.strip()
                result[label] = value

            result["Work Type"] = self._get_work_type()
            result["Experience Level"] = self._get_experience_level()
            result["Study level"] = self._get_education_level()
            return result
        except NoSuchElementException:
            return "NO INFORMATION"

