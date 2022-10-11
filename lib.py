import chromedriver_binary # This adds chrome to PATH (somehow...)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def get_cards(url:str, cookies: dict | None =None, selenium_opts: Options|None=None):
    if not selenium_opts:
        _selenium_opts = Options()
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        _selenium_opts.headless = True
        _selenium_opts.add_argument(f"user-agent={user_agent}")
        _selenium_opts.add_argument(f"--window-size=1920,1080")
        _selenium_opts.add_argument(f"start-maximized")
    else:
        _selenium_opts = selenium_opts
    driver = webdriver.Chrome(options=_selenium_opts)
    if cookies:
        driver.add_cookie(cookies)
    driver.get(url)
    elems = driver.find_elements(By.CSS_SELECTOR,"span.TermText.notranslate.lang-en")
    elems_text = [elem.text for elem in elems]
    return {elems_text[i * 2]: elems_text[i*2 + 1] for i in range(len(elems_text)//2)}

if __name__ == "__main__":
    # URL = "https://quizlet.com/324497972/acbs-160-final-exam-flash-cards/"
    # URL = "https://quizlet.com/436919487/acbs-160-midterm-quizzes-on-track-s-flash-cards/"
    URL="https://quizlet.com/231851219/animal-midterm-flash-cards/"
    cards = get_cards(URL)
    print(cards)
    print(f"A total of: {len(cards)} cards")

