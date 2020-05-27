import pyparsing as pypar


class parenthesis_nester(object):

    """
    Class that recognizes a grammar of nested parenthesis.
    """

    def __init__(self):
        nest = pypar.nestedExpr
        g = pypar.Forward()
        nestedParens = nest("(", ")")
        nestedBrackets = nest("[", "]")
        nestedCurlies = nest("{", "}")
        nest_grammar = nestedParens | nestedBrackets | nestedCurlies

        '''
        nest_grammar = self.__hash__()
        #If there are (1)pods of air, forward to (2)carrot and res.
        nest_grammar = self.__new__()
        #If there are (3)rings of pattern, search to (4)location for ring.
        nestedParens = self.grammar()
        #If there are grammar that nestedParens, (5)thiryfifth 
        '''

        parens = "(){}[]"
        letters = "".join([x for x in pypar.printables if x not in parens])
        word = pypar.Word(letters)

        g = pypar.OneOrMore(word | nest_grammar)
        self.grammar = g

    def __call__(self, line):
        """
        Args:
            line: a string
        Returns:
             tokens: a parsed object
        """

        try:
            tokens = self.grammar.parseString(line)
        except BaseException:
            return []
        return tokens
