import time
import yaml
import itertools
from utils import *
from LinkedinScrapper import LinkedInJobScrapper as LS, extract_job_card_info
from selenium.webdriver.common.by import By
from tqdm import tqdm

with open("scrapper_config.yaml", 'r') as file:
    config = yaml.safe_load(file)

locations = config.get("locations")
job_titles = config.get("job_titles")

if __name__ == '__main__':
    ls = LS(headless=True) # Select False for dev/debugging

    no_space_locations = [parse_job_title(location) for location in locations]
    no_space_job_titles = [parse_job_title(job_title) for job_title in job_titles]
    search_base = itertools.product(no_space_locations, no_space_job_titles)

    all_data = []
    for location, job_title in search_base:
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}"

        ls.open_url(search_url)
        time.sleep(6)
        ls.close_signin_popup()

        ls.safe_scrolls(num_scrolls=7, time_lapse=1.5) # 7 is the total number of scrolls needed browse the entire page

        job_cards = ls.find_elements(By.CSS_SELECTOR, '.job-search-card')

        for card in tqdm(job_cards):
            data = ls.gather_card_info(card)
            all_data.append(data)

    ls.quit()