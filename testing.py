import math
import nltk
from nltk.metrics.association import BigramAssocMeasures

message = "1 2 3 4 5. 1 2 3 4. 1 2 3. 1 2. 1."
words = nltk.word_tokenize(message)

bi = nltk.BigramCollocationFinder.from_words(words)
tri = nltk.TrigramCollocationFinder.from_words(words)
quad = nltk.QuadgramCollocationFinder.from_words(words)

bigram = bi.score_ngrams(BigramAssocMeasures.likelihood_ratio)
trigram = tri.score_ngrams(nltk.TrigramAssocMeasures.likelihood_ratio)
quadgram = quad.score_ngrams(nltk.QuadgramAssocMeasures.likelihood_ratio)

weightFn = lambda x: math.log(x + 1)
ngramFn = lambda ngram: (ngram[0], ngram[1] * weightFn(len(ngram[0])))

ngrams = list(map(ngramFn, bigram + trigram + quadgram))
ngrams.sort(key=lambda ngram: ngram[1], reverse=True)
print(list(map(lambda ngram: ngram[0], ngrams))[0:10])

