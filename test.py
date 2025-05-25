from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import os
import random
from datetime import datetime
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LinkedInJobScraper:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(1920, 1080)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        logging.info("Navigateur initialisé")

    def close(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
            logging.info("Navigateur fermé")

    def search_jobs(self, job_title, location="Morocco", pages=3):
        seen_jobs = set()
        all_jobs = []
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={job_title.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
        logging.info(f"Navigation vers : {search_url}")
        self.driver.get(search_url)
        time.sleep(4)

        for _ in range(pages):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
            logging.info(f"{len(job_cards)} offres détectées")

            for card in job_cards:
                try:
                    job_url = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    if job_url in seen_jobs:
                        continue
                    seen_jobs.add(job_url)

                    job_data = self._extract_job_card_info(card)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    card.click()
                    time.sleep(2)
                    print(f"\n🔎 Viewing job: {job_data['Job Title']} at {job_data['Company Name']}\n")

                    job_data["Work Type"] = self._get_work_type()
                    job_data["Experience Level"] = self._get_experience_level()
                    job_data["Niveau d'étude"] = self._get_education_level()
                    all_jobs.append(job_data)

                    time.sleep(random.uniform(1, 2))
                except Exception as e:
                    logging.warning(f"Erreur carte offre : {e}")
                    continue
        return all_jobs

    def _extract_job_card_info(self, card):
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

    def _get_work_type(self):
        try:
            items = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'job-insight')]")
            for item in items:
                txt = item.text.strip().lower()
                if "distance" in txt:
                    return "À distance"
                if "hybride" in txt:
                    return "Hybride"
                if "présentiel" in txt:
                    return "Présentiel"
            return "Inconnu"
        except:
            return "Inconnu"

    def _get_experience_level(self):
        try:
            desc = self.driver.find_element(By.CSS_SELECTOR, ".show-more-less-html__markup").text
            if re.search(r"\binternship\b", desc, re.IGNORECASE):
                return "Internship"
            if re.search(r"\bentry level\b", desc, re.IGNORECASE):
                return "Entry level"
            match = re.search(r"(\d+)\+?\s*(ans|years)", desc, re.IGNORECASE)
            if match:
                return f"{match.group(1)}+ years"
        except:
            pass
        return "Unknown"

    def _get_education_level(self):
        try:
            desc = self.driver.find_element(By.CSS_SELECTOR, ".show-more-less-html__markup").text
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
        except:
            pass
        return "Inconnu"

def main():
    job_titles = ["Data Engineer", "Business Intelligence Analyst", "Machine Learning Engineer", "Cybersecurity Engineer", "Software Engineer"]
    locations = ["Morocco", "France", "Canada", "China"]
    scraper = LinkedInJobScraper(headless=False)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = f"linkedin_jobs_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    all_jobs = []
    try:
        for location in locations:
            for job_title in job_titles:
                logging.info(f"📍 {job_title} @ {location}")
                jobs = scraper.search_jobs(job_title, location=location, pages=10)
                if jobs:
                    df = pd.DataFrame(jobs)
                    file_path = os.path.join(output_dir, f"{job_title.replace(' ', '_')}_{location.replace(' ', '_')}.csv")
                    df.to_csv(file_path, index=False)
                    all_jobs.extend(jobs)
                    logging.info(f"✅ Enregistré {len(jobs)} offres à {file_path}")
                else:
                    logging.info("❌ Aucune offre trouvée")

    finally:
        scraper.close()

    if all_jobs:
        df_all = pd.DataFrame(all_jobs)
        df_all.to_csv(os.path.join(output_dir, "all_jobs.csv"), index=False)
        logging.info(f"📦 Total : {len(all_jobs)} offres enregistrées dans all_jobs.csv")

if __name__ == "__main__":
    main()
