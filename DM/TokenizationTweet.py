import nltk


class TokenizationTweet():
    # kelime koku
    def stemmerTrFps6(term):
        return term[:6]

    def stem_tokens(tokens, stemmer):
        stemmed = []
        for item in tokens:
            stemmed.append(stemmer(item))
        return stemmed

    def tokenize(text):
        stemmer = TokenizationTweet.stemmerTrFps6
        tokens = nltk.word_tokenize(text)
        stems = TokenizationTweet.stem_tokens(tokens, stemmer)
        return stems
