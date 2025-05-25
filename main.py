import time
from LinkedinScrapper import LinkedInJobScrapper as LS

if __name__ == '__main__':
    ls = LS(headless=False) # Select False for dev/debugging

    location = "Morocco"
    job_title = "Data Engineer"

    no_space_location = location.replace(" ", "%20")
    no_space_job_title = job_title.replace(" ", "%20")

    search_url = f"https://www.linkedin.com/jobs/search/?keywords={no_space_job_title}&location={no_space_location}"

    ls.open_url(search_url)
    ls.close_signin_popup()

    time.sleep(5)

    ls.quit()