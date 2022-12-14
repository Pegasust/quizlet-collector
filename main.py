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
    processed_question = sentence_tokens(question)
    return Card(url, question, answer, ' '.join(processed_question))

def sentence_tokens(sentence: str):
    """
    Returns a string of meaning for a given sentence
    """
    meaning_tokens = re.split('[^a-zA-Z0-9]', sentence)
    meaning_tokens = [q.lower() for q in meaning_tokens if len(q) >= 1]
    return meaning_tokens
    
import multiprocessing

def _get_cards(prop):
    (url, cookies, sel_opts) = prop
    retval = (url, lib.get_cards(url, cookies, sel_opts))
    return retval

def get_cards(urls: list[str], cookies:dict|None = None, selenium_opts:Options|None=None):
    """
    Main function to gather cards from different URLs
    """
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

def pp_cards(cards: list[Card]):
    """
    Pretty print the list of cards
    """
    fmt_cards = "\n".join([
        f"{i}. \"{card.processed_question}\"\n - \"{card.answer}\"" 
        for i, card in enumerate(cards)
    ])
    return fmt_cards

def proc_q_to_q(proc_q: str, proc_q_lookup: dict[str, list[Card]]):
    return next(card.question 
        for card in proc_q_lookup[proc_q] if card.processed_question == proc_q)

def url_and_ans(cards: list[Card]): 
    """
    Pretty prints answers and cite url where the answers are from
    """
    # attempt to dedup meaning of answers
    if any((cards[i].processed_question != cards[i-1].processed_question 
               for i in range(1, len(cards)))):
        # cards contain different questions, so it's not safe to group similar answers together
        return "\n".join([
            f" - \"{card.answer}\" ({card.url})"
            for card in cards
        ])
    ans_meaning_to_cards = dict()
    for card in cards:
        ans_meaning = " ".join(sentence_tokens(card.answer))
        if ans_meaning not in ans_meaning_to_cards:
            ans_meaning_to_cards[ans_meaning] = []
        ans_meaning_to_cards[ans_meaning].append(card)
    group_urls = lambda cards: " ".join((card.url for card in cards))
    first_meaning = lambda meaning: ans_meaning_to_cards[meaning][0].answer
    return "\n".join([
        f"- \"{first_meaning(meaning)}\" ({group_urls(cards)})"
        for meaning, cards in ans_meaning_to_cards.items()
    ])

def pp_proc_questions(proc_q_lookup: dict[str, list[Card]]):
    """
    Pretty prints the processed questions (dedup from sentence_value())
    """
    return "\n".join([
        f"{i}. {proc_q_to_q(proc_q, proc_q_lookup)}\n{url_and_ans(cards)}"
        for i, (proc_q, cards) in enumerate(proc_q_lookup.items())
    ])


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
    # URLS = ["https://quizlet.com/231851219/animal-midterm-flash-cards/"]
    (cards, url_lookup, proc_q_lookup) = get_cards(URLS)
    # more_than_1_answer = {_q: cards 
    #     for _q, cards in proc_q_lookup.items() if len(cards) > 1}
    # print(pp_proc_questions(more_than_1_answer))
    # print(f"{len(more_than_1_answer)}/{len(proc_q_lookup)} processed questions with more than 1 answer")
    print(pp_proc_questions(proc_q_lookup))




