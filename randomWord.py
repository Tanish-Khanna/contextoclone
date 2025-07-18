import random
import logging
import config

logger = logging.getLogger(__name__)


def randomWord():
    with open("wordlist/filtered_oxford_3000.txt", "r") as file:
        word_list = file.read().splitlines()
        a = random.choice(word_list)
        if config.DEBUG_RANDOM_WORD:
            logger.debug("the random word is %s", a)
    return a
