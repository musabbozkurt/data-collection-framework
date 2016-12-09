import re

import GraduationProject
from DM import ConfigParser


class TokenizationTextFile():

        tokens_re = re.compile(r'(' + '|'.join(ConfigParser.regex_str) + ')', re.VERBOSE | re.IGNORECASE)
        emoticon_re = re.compile(r'^' + ConfigParser.emoticons_str + '$', re.VERBOSE | re.IGNORECASE)

        def preprocess(s, lowercase=False):
            tokens = TokenizationTextFile.tokens_re.findall(s)
            if lowercase:
                tokens = [token if TokenizationTextFile.emoticon_re.search(token) else token.lower() for token in tokens]
                GraduationProject.logger.info("Preprocess function is called it preserves eyes,nose,urls mouth ... etc")
            return tokens