import datetime as a
from datetime import datetime
fmt = '%Y-%m-%d %H:%M:%S'
d1 = datetime.strptime(a.datetime.now().strftime(fmt), fmt)
d2 = datetime.strptime('2016-12-16 17:31:22', fmt)

print ((d2-d1).days * 24 * 60)

from nltk import ngrams
sentence = 'I do not like green eggs and ham, I do not like them Sam I am!'
n = 4
sixgrams = ngrams(sentence.split(), n)
for grams in sixgrams:
  print(grams)
from DM import NGrams as ngram

ngram.NGrams.ngrams(sentence,4)

print(64*'a')
from nltk.collocations import *
import nltk
#You should tokenize your text
text = "I do not like green eggs and ham, I do not like them Sam I am!"
tokens = nltk.wordpunct_tokenize(text)
fourgrams=nltk.collocations.QuadgramCollocationFinder.from_words(tokens,window_size=4)
for fourgram, freq in fourgrams.ngram_fd.items():
   print (fourgram, freq)