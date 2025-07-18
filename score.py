import numpy as np
import config
from gensim.models import KeyedVectors

model = KeyedVectors.load_word2vec_format('models/glove.6B.50d.word2vec.txt', binary=False)
glove_vocab = set(model.key_to_index.keys())

def cosine_similarity(vec1, vec2):
  dp = np.dot(vec1, vec2)
  #norm is essentially magnitude.
  norm1 = np.linalg.norm(vec1)
  norm2 = np.linalg.norm(vec2)
  return dp / (norm1 * norm2)


def scorer(word1, target_word):
    """Return True if the guess matches the target within tolerance."""
    try:
        vec1 = model[word1]
        vec_target = model[target_word]

        similarity = cosine_similarity(vec1, vec_target)
        print(f"cosine similarity: {similarity:.5f}")

        return 1 - config.WINNING_TOLERANCE <= similarity <= 1 + config.WINNING_TOLERANCE

    except KeyError:
        print(f"Error: '{word1}' is not in the vocabulary.")
        return False
