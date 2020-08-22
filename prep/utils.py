import re
import string


def is_binary(series, allow_na=False):
    if allow_na:
        series.dropna(inplace=True)
    return sorted(series.unique()) == [0, 1]

RE_EMAIL = re.compile(
    r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*)@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])")
RE_URL = re.compile(r"((https?|ftp|smtp):\/\/)?(www.)?[a-z0-9]+\.[a-z]+(\/[a-zA-Z0-9#]+\/?)*")
RE_RELAX_PHONE = re.compile('(\(? ?[\d]{2,3} ?\)?.{,3}?){2,}')
# Taken from:
# http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf
# Line matches the regular expression "^[\s]*---*[\s]*$".
RE_SEPARATOR = re.compile('^[\s]*---*[\s]*')
RE_REPLY = re.compile('^\>')
RE_REPLY_PUNCT = re.compile('^[^A-Za-z0-9]{1,2}\>')
RE_TAB = re.compile('\t')
RE_WROTE = re.compile('\s(wr[oi]tes?:)$')

# Taken from:
# http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf
# Line has a sequence of 10 or more special characters.
RE_SPECIAL_CHARS = re.compile(('^[\s]*([\*]|#|[\+]|[\^]|-|[\~]|[\&]|[\$]|_|[\!]|'
                               '[\/]|[\%]|[\:]|[\=]){10,}[\s]*$'))

RE_SIGNATURE_WORDS = re.compile(('(T|t)hank.*,|(B|b)est|(R|r)egards|'
                                 '^sent[ ]{1}from[ ]{1}my[\s,!\w]*$|BR|(S|s)incerely|'
                                 '(C|c)orporation|Group'))

# Taken from:
# http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf
# Line contains a pattern like Vitor R. Carvalho or William W. Cohen.
RE_NAME = re.compile('[A-Z][a-z]+\s\s?[A-Z][\.]?\s\s?[A-Z][a-z]+')

ENTITY_PATTERN = "^#sig#"


def punct_percent(line):
    if len(line) == 0:
        return 0
    punct = [c for c in line if c in string.punctuation]
    return len(punct) / len(line)


def alphanum_percent(line):
    if len(line) == 0:
        return 0
    punct = [c for c in line if c.isalnum()]
    return len(punct) / len(line)


feature_dict = {
        'email': lambda doc: 1 if RE_EMAIL.search(doc[0]) else 0,
        'url': lambda doc: 1 if RE_URL.search(doc[0]) else 0,
        'phone': lambda doc: 1 if RE_RELAX_PHONE.search(doc[0]) else 0,
        'sigdelimiter': lambda doc: 1 if RE_SEPARATOR.match(doc[0]) else 0,
        'special': lambda doc: 1 if RE_SPECIAL_CHARS.search(doc[0]) else 0,
        'words': lambda doc: 1 if RE_SIGNATURE_WORDS.search(doc[0]) else 0,  # keywords like "regards" and others
        'name': lambda doc: 1 if RE_NAME.search(doc[0]) else 0,
        'endquote': lambda doc: 1 if doc[0].endswith("\"") else 0,
        'tabs1': lambda doc: 1 if len(RE_TAB.findall(doc[0])) == 1 else 0,
        'tabs2': lambda doc: 1 if len(RE_TAB.findall(doc[0])) == 2 else 0,
        'tabs3': lambda doc: 1 if len(RE_TAB.findall(doc[0])) >= 3 else 0,
        'punct20': lambda doc: 1 if punct_percent(doc[0]) >= 0.2 else 0,
        'punct50': lambda doc: 1 if punct_percent(doc[0]) >= 0.5 else 0,
        'punct90': lambda doc: 1 if punct_percent(doc[0]) >= 0.9 else 0,
        'reply': lambda doc: 1 if RE_REPLY.match(doc[0]) else 0,
        'startpunct': lambda doc: 1 if doc[0].startswith(tuple(p for p in string.punctuation)) else 0,
        'firstchar': lambda doc: doc[0][0] if len(doc[0]) > 0 else "",
        'replypunct': lambda doc: 1 if RE_REPLY_PUNCT.match(doc[0]) else 0,
        'wrote': lambda doc: 1 if RE_WROTE.search(doc[0]) else 1,
        'alphanum90': lambda doc: 1 if alphanum_percent(doc[0]) < 0.9 else 0,
        'alphanum50': lambda doc: 1 if alphanum_percent(doc[0]) < 0.5 else 0,
        'alphanum10': lambda doc: 1 if alphanum_percent(doc[0]) < 0.1 else 0,
        'title': lambda doc: 1 if doc[0].strip().istitle() else 0
    }


def line_to_entity(line, filename, i):
    m = re.match(ENTITY_PATTERN, line)
    if m:
        e = {
            "line": line[5:],
            "filename": filename,
            "entity": "signature",
            "len": len(line[5:]),
            "lineNo": i+1
        }
    else:
        e = {"line": line, "filename": filename, "entity": "no_entity", "len": len(line), "lineNo": i+1}
    doc = tuple((e["line"],))
    for feature, fn in feature_dict.items():
        e[feature] = fn(doc)
    return e


def remove_blanks(lines):
    return [line for line in lines if len(line.strip()) > 0]


def get_signature_length(ents):
    """ Signature length in number of lines """
    return sum(1 for e in ents if e["entity"] == "signature")


def strip_blank_lines(lines, leading=True, trailing=True):
    leading_blank = 0
    trailing_blank = len(lines)
    lines_it = iter(lines)
    next_line = next(lines_it, None)
    while next_line is not None and len(next_line.strip()) == 0:
        leading_blank += 1
        next_line = next(lines_it, None)

    if trailing:
        it_reversed = iter(reversed(lines))
        next_line = next(it_reversed, None)
        while next_line is not None and len(next_line.strip()) == 0:
            trailing_blank -= 1
            next_line = next(it_reversed, None)
    return lines[leading_blank:trailing_blank]


if __name__ == "__main__":
    lines = [
        "  ",
        "Lisa,",
        "",
        "I apologize for the delay!  This is a new one for us and they are taking their sweet time on getting the paper work back to us.  I have copied Pam LaRue on this email as you can see and she will respond to you on how that process is going.",
        "              ",
        "#sig#Rhonda",
        "",
        "  "
    ]
    remove_leading = strip_blank_lines(lines)
    print()

    import numpy as np
    l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    r = np.arange(0, 1, .25)
    print(r)
    print(np.quantile(l, r))
    print(np.median(l))
