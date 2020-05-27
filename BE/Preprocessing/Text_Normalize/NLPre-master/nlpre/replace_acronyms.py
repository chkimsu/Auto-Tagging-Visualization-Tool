import nlpre.identify_parenthetical_phrases as IPP
import collections
import logging
from . import nlp


class replace_acronyms(object):

    """
    Replaces acronyms and abbreviations found in a document with their
    corresponding phrase. A counter dictionary is passed in __init__
    to determine phrases.

    If an acronym is explicitly identified with a phrase in a document, then
    all instances of that acronym in the document will be replaced with the
    given phrase.

    Example:
        input: "The Environmental Protection Agency (EPA) protects trees. The
                EPA was created by Nixon"
        output: "The Environmental Protection Agency
                 (Environmental_Protection_Agency) protects trees. The
                 Environmental_Protection_Agency was created by Nixon"

    If there is no explicit indication what the phrase is within the document,
    then the most common phrase associated with the acronym in the given
    counter is used.

    Example:
        input: "The EPA protects trees"
        output: "The Environmental_Protection_Agency protects trees"
    """

    def __init__(
        self,
        counter=None,
        prefix=None,
        suffix=None,
        underscore=True,
        preprocessed=False,
        use_most_common=False,
    ):
        """
        Initialize the parser, the acronym dictionary, and flags

        Args:
            counter: A counter object of acronyms and their counts found in a
                     larger corpus
            underscore: A boolean to indicate whether to insert phrases
                        as a single underscored token
            preprocessed: A boolean to indicate if input text is raw,
                          or has been processed by other NLPre modules
            use_most_common: A boolean to indicate if the phrase is replaced
                          by the most common one, regardless if it is found
                          within the current document
        """
        self.logger = logging.getLogger(__name__)

        self.prefix = prefix
        self.suffix = suffix
        self.underscore = underscore
        self.preprocessed = preprocessed
        self.use_most_common = use_most_common
        self.IPP = IPP.identify_parenthetical_phrases()
        self.acronym_dict = {}

        self.counter = counter
        self._build_acronym_dict(counter)

    def _build_acronym_dict(self, counter):

        if counter is None:
            return

        for acronym_tuple, count in counter.items():
            if acronym_tuple[1] in self.acronym_dict:
                self.acronym_dict[acronym_tuple[1]][acronym_tuple[0]] = count
            else:
                results = collections.Counter()
                results[acronym_tuple[0]] = count
                self.acronym_dict[acronym_tuple[1]] = results

    def check_self_counter(self, token, doc_counter):
        """
        Check if an acronym token is defined within the document

        Args:
            token: a string token
            doc_counter: a counter object of acronyms defined within a document
        Returns:
            a boolean
        """

        for acronym_tuple in doc_counter.keys():
            if acronym_tuple[1] == token:
                highest_phrase = list(acronym_tuple[0])
                return highest_phrase
        return False

    def word_belongs(self, word, acronym_phrases):
        """
        Return false if a word cannot belong to any abbreviated phrase.
        Since words with dashes are turned into a list of their
        individual words, we must treat all words as a list. So, single
        tokens are converted to single item lists.

        Args:
            word: a string token
            acronym_phrases: a 2D list of string tokens
        Returns:
            a boolean
        """
        for acronym_phrase in acronym_phrases:

            if isinstance(word, str):
                wordlist = [word]
            else:
                wordlist = list(word)

            word_included = all(x not in acronym_phrases for x in wordlist)

            if word_included:
                return True

        return False

    def check_acronym(self, token):
        """
        Check if a token is an acronym to be replaced

        Args:
            token: a string token
        Returns:
            a boolean
        """

        if token.lower() == token:
            return False

        return token in self.acronym_dict

    def check_phrase(self, token, pos, tokens, counter):
        """
        Determine if a series of tokens, starting with the input token, form
        an acronym phrase found in the counter. If the token does not form
        a phrase, the function returns as false.

        Args:
            token: a string token
            pos: an int
            tokens: a list of string tokens
            counter: a counter of acronym's and associated phrases
        Returns:
            output: a string the tokens that make up an acronym phrases,
                    connected by an underline
            If no valid output exists, a boolean False is returned

        """
        if not self.underscore:
            return False

        acronym_phrases = []

        for acronym_tuple in counter.keys():
            acronym_phrases.append(list(acronym_tuple[0]))

        phrase = []
        word = token
        length = 0
        while pos < len(tokens) - 1:
            length += 1
            if "-" in word:
                word = word.split("-")
                phrase.extend(word)
            else:
                phrase.append(word)

            if not self.word_belongs(word, acronym_phrases):
                return False

            if phrase in acronym_phrases:
                output = ("_".join(phrase), length - 1)
                return output
            else:
                pos += 1
                word = tokens[pos]

        return False

    def __call__(self, document, doc_counter=None):
        """
        Identify and replace all acronyms in the document

        Args:
            document: a string
            doc_counter: a counter object of acronyms defined within a
                         document. If missing, identify_parenthetical_phrases
                         is run.
        Returns:
            new_doc: a string
        """

        if doc_counter is None:
            doc_counter = self.IPP(document)
            self._build_acronym_dict(doc_counter)

        if self.preprocessed:
            parsed = document.split("\n")
        else:
            document = " ".join(document.strip().split())
            parsed = [sent for sent in nlp(document, disable=["tagger"]).sents]

        new_doc = []

        for sentence in parsed:

            if self.preprocessed:
                tokens = sentence.split()
            else:
                tokens = [x.text for x in sentence]

            new_sentence = []

            index = -1
            while index < len(tokens) - 1:
                index += 1
                token = tokens[index]

                if self.check_acronym(token):

                    # check if acronym is used within document
                    highest_phrase = self.check_self_counter(token, doc_counter)

                    # If not found, replace with the original token
                    if not highest_phrase and not self.use_most_common:
                        new_sentence.append(token)
                        continue

                    if not highest_phrase:
                        acronym_counts = self.acronym_dict[token]
                        highest_phrase = list(
                            acronym_counts.most_common(1)[0][0]
                        )

                    if self.underscore and self.prefix:
                        highest_phrase.insert(0, self.prefix)

                    if self.underscore and self.suffix:
                        highest_phrase.append(self.suffix)

                    if self.underscore:
                        highest_phrase = "_".join(highest_phrase)
                        self.logger.info(
                            "Replacing token %s with phrase %s"
                            % (token, highest_phrase)
                        )
                        new_sentence.append(highest_phrase)
                    else:
                        self.logger.info(
                            "Replacing token %s with phrase %s"
                            % (token, highest_phrase)
                        )
                        new_sentence.extend(highest_phrase)
                    continue

                # Note: this code is case sensitive. Tokens will not be
                # recognized as being acronym phrases if their capitalization
                # is different from the phrases found in identify_parenthetical
                # _phrases.py
                #
                # This is particularly an issue with titlecaps.py, which might
                # force phrase tokens to lowercase
                tokenized_phrase = self.check_phrase(
                    token, index, tokens, doc_counter
                )

                if tokenized_phrase:
                    phrase = tokenized_phrase[0]
                    if self.prefix:
                        phrase = "_".join([self.prefix, phrase])

                    if self.suffix:
                        phrase = "_".join([phrase, self.suffix])

                    self.logger.info("Tokenizing phrase %s" % phrase)
                    new_sentence.append(phrase)
                    index += tokenized_phrase[1]
                else:
                    new_sentence.append(token)
            new_doc.append(" ".join(new_sentence))

        new_doc = "\n".join(new_doc)

        return new_doc
