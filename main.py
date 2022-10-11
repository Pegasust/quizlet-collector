from selenium.webdriver.chrome.options import Options
import lib
import re
from dataclasses import dataclass

@dataclass
class Card:
    url: str
    question: str
    answer: str
    processed_question: str

def createCard(url: str, question: str, answer: str) -> Card:
    processed_question = proc_q(question)
    return Card(url, question, answer, ' '.join(processed_question))

def proc_q(question: str):
    processed_question = re.split('[^a-zA-Z0-9]', question)
    processed_question = [q.lower() for q in processed_question if len(q) >= 1]
    return processed_question
    
import multiprocessing

def _get_cards(prop):
    (url, cookies, sel_opts) = prop
    retval = (url, lib.get_cards(url, cookies, sel_opts))
    return retval

def get_cards(urls: list[str],cookies:dict|None = None, selenium_opts:Options|None=None):
    try:
        cpus = multiprocessing.cpu_count()
    except NotADirectoryError:
        cpus = 2
    print(f"CPUs: {cpus}")
    pool = multiprocessing.Pool(processes=cpus)
    props = [(url, cookies, selenium_opts) for url in urls]
    
    card_url = pool.map(_get_cards, props)

    url_lookup: dict[str, list[Card]] = dict()
    proc_q_lookup: dict[str, list[Card]] = dict()
    cards: list[Card] = []
    for (url, _cards) in card_url:
        print(f"cards len: {len(_cards)}")
        cards_vect = [createCard(url, qu, ans) for qu, ans in _cards.items()]
        print(f"cards_vect: {len(cards_vect)}")
        cards.extend(cards_vect)
        url_lookup[url] = cards_vect
        for card in cards_vect:
            if len(card.processed_question) < 2:
                # blank
                continue
            if card.processed_question not in proc_q_lookup:

                proc_q_lookup[card.processed_question] = []
            proc_q_lookup[card.processed_question].append(card)
    return (cards, url_lookup, proc_q_lookup)

if __name__ == "__main__":
    URLS = [
        "https://quizlet.com/555255851/acbs-160-midterm-study-guide-flash-cards/",
        "https://quizlet.com/436919487/acbs-160-midterm-quizzes-on-track-s-flash-cards/",
        "https://quizlet.com/231851219/animal-midterm-flash-cards/",
        "https://quizlet.com/506249434/acbs-final-review-flash-cards/",
        "https://quizlet.com/231348833/acbs-midterm-flash-cards/",
        "https://quizlet.com/251455660/acbs-160d1-flash-cards/",
        "https://quizlet.com/324497972/acbs-160-final-exam-flash-cards/",
        "https://quizlet.com/350653247/acbs-final-flash-cards/",
        "https://quizlet.com/230677694/acbs-midterm-1-flash-cards/",
        "https://quizlet.com/252056684/acbs-160-quizzes-flash-cards/",
        "https://quizlet.com/249104008/human-animal-final-flash-cards/",
        "https://quizlet.com/231579852/acbs-quiz-questions-flash-cards/",
    ]
    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    # URLS = ["https://quizlet.com/231851219/animal-midterm-flash-cards/"]
    (cards, url_lookup, proc_q_lookup) = get_cards(URLS)
    more_than_1_answer = [cards for _q, cards in proc_q_lookup.items() if len(cards) > 1]
    url_and_ans = lambda cards: "\n".join([
                                            f" - {card.answer} ({card.url})"
                                            for card in cards
                                          ])
    proc_q_to_q = lambda proc_q: next(card.question 
        for card in proc_q_lookup[proc_q] if card.processed_question == proc_q)
    print(f"{len(more_than_1_answer)}/{len(proc_q_lookup)} processed questions with more than 1 answer")
    print("\n".join([
                        f"*****\n{proc_q_to_q(proc_q)}:\n{url_and_ans(cards)}\n*****"
                        for proc_q, cards in proc_q_lookup.items()
                        if len(cards) > 1
                    ]))

    fmt_cards = "\n".join([
                              f"{i}. \"{card.processed_question}\"\n - \"{card.answer}\"" 
                              for i, card in enumerate(cards)])
    print(f"*** Cards ***\n{fmt_cards}")



