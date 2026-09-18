import numpy as np
from gensim.models import KeyedVectors

model = KeyedVectors.load_word2vec_format(
    "models/glove.6B.50d.word2vec.txt", binary=False
)


def cosine_similarity(vec1, vec2):
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


def generate_rankings(target_word, vocab):
    target_vector = model[target_word]
    scores = {}
    for word in vocab:
        if word not in model:
            continue
        scores[word] = cosine_similarity(target_vector, model[word])

    ordered = sorted(scores, key=scores.get, reverse=True)
    return {word: rank + 1 for rank, word in enumerate(ordered)}
