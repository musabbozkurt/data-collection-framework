import json
import operator
import re
import string
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
from nltk.corpus import stopwords

from d_c_f.config import ConfigParser


class TermFreqAndAllTerms:
    emoticons_str = ConfigParser.emoticons_str
    regex_str = [emoticons_str,
                 ConfigParser.HTML_tags,  # HTML tags
                 r'(?:@[\w_]+)',  # @-mentions
                 r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
                 r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs

                 r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
                 r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
                 r'(?:[\w_]+)',  # other words
                 r'(?:\S)'  # anything else
                 ]

    # print(regex_str)
    # print(emoticons_str)

    tokens_re = re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)
    emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)

    def preprocess(s, lowercase=False):
        tokens = TermFreqAndAllTerms.tokens_re.findall(s)
        if lowercase:
            tokens = [token if TermFreqAndAllTerms.emoticon_re.search(token) else token.lower() for token in tokens]
        return tokens

    def term_counter(fname, inputforMostcommon):
        fname = ConfigParser.streamingTxtFile
        with open(fname, 'r') as f:
            count_all = Counter()
            for line in f:
                tweet = json.loads(line)
                # Create a list with all the terms
                terms_all = [term for term in TermFreqAndAllTerms.preprocess(tweet['text'])]
                # Update the counter
                count_all.update(terms_all)
            # Print the first 5 most frequent words
            # print(count_all)
            print('FIRST ' + str(inputforMostcommon) + ' MOST FREQUENT WORDS ARE BELOW')
            print("The most frequent words (or should I say, tokens), are not exactly meaningful.")
            print(count_all.most_common(inputforMostcommon))

        punctuation = list(string.punctuation)
        stop = stopwords.words('english') + punctuation + ['rt', 'via']
        terms_stop = [term for term in TermFreqAndAllTerms.preprocess(tweet['text']) if term not in stop]
        print('ALL STOP TERMS ARE BELOW ')
        print(terms_stop)

        # Count terms only once, equivalent to Document Frequency
        terms_single = set(terms_all)
        print('COUNT TERMS ONLY ONCE SINGLE TERMS ARE BELOW')
        print(terms_single)

        # Count hashtags only
        terms_hash = [term for term in TermFreqAndAllTerms.preprocess(tweet['text'])
                      if term.startswith('#')]
        print('ALL HASHTAG TERMS ARE BELOW. ')
        print(terms_hash)

        # Count terms only (no hashtags, no mentions)
        terms_only = [term for term in TermFreqAndAllTerms.preprocess(tweet['text'])
                      if term not in stop and
                      not term.startswith(('#', '@'))]

        print('ALL TERMS ARE BELOW THERE IS NO HASHTAGS OR MENTIONS')
        print(terms_only)

    def semantic(search_word, fname, inputforMostCommon, termMax):

        from collections import defaultdict
        # remember to include the other import from the previous post

        com = defaultdict(lambda: defaultdict(int))
        punctuation = list(string.punctuation)
        stop = stopwords.words('english') + punctuation + ['rt', 'via']

        # f is the file pointer to the JSON data set
        with open(fname, 'r') as f:
            count_all = Counter()
            for line in f:
                tweet = json.loads(line)
                # Create a list with all the terms
                terms_all = [term for term in TermFreqAndAllTerms.preprocess(tweet['text'])]
                # Update the counter
                count_all.update(terms_all)
                terms_only = [term for term in TermFreqAndAllTerms.preprocess(tweet['text'])
                              if term not in stop
                              and not term.startswith(('#', '@'))]
                print('ALL TERMS ARE BELOW')
                print(terms_only)

                # Build co-occurrence matrix
                for i in range(len(terms_only) - 1):
                    for j in range(i + 1, len(terms_only)):
                        w1, w2 = sorted([terms_only[i], terms_only[j]])
                        if w1 != w2:
                            com[w1][w2] += 1

                com_max = []

                # For each term, look for the most common co-occurrent terms
                for t1 in com:
                    t1_max_terms = sorted(com[t1].items(), key=operator.itemgetter(1), reverse=True)[:5]
                    for t2, t2_count in t1_max_terms:
                        com_max.append(((t1, t2), t2_count))

                # Get the most frequent co-occurrences
                terms_max = sorted(com_max, key=operator.itemgetter(1), reverse=True)
                print('THE MOST FREQUENT CO-OCCURRENCES ARE BELOW')
                print(terms_max[:termMax])

                # search_word  # pass a term as a command-line argument
                count_search = Counter()
                for line in f:
                    tweet = json.loads(line)
                    terms_only = [term for term in TermFreqAndAllTerms.preprocess(tweet['text'])
                                  if term not in stop
                                  and not term.startswith(('#', '@'))]
                    if search_word in terms_only:
                        count_search.update(terms_only)

                print("Co-occurrence for %s:" % search_word)
                print(count_search.most_common(inputforMostCommon))

                names, values = zip(*terms_max)
                ind = np.arange(len(terms_max))  # the x locations for the groups
                width = 0.70  # the width of the bars

                fig, ax = plt.subplots()
                rects1 = ax.bar(ind, values, width, color='r')

                # add some text for labels, title and axes ticks
                ax.set_ylabel('Count')
                ax.set_xticks(ind + width / 2.)
                ax.set_xticklabels(names)

                def autolabel(rects):
                    # attach some text labels
                    for rect in rects:
                        height = rect.get_height()
                        ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                                '%d' % int(height),
                                ha='center', va='bottom')

                autolabel(rects1)

                # plt.show()
