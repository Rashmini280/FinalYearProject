from pydoc import text
import re

ENGLISH_PROTECTED = {"the", "a", "an", "and", "breaking", "news", "official"}

def looks_like_singlish(token):
    markers = ["aa", "ee", "oo", "uu", "nnd", "nng", "mko", "khmd"]
    return any(m in token.lower() for m in markers)

def selective_singlish_normalize(text, normalizer):
    tokens = text.split()
    output = []
    for t in tokens:
        if t[0].isupper() and not looks_like_singlish(t):
            output.append(t)
        elif looks_like_singlish(t) or not t.lower() in ENGLISH_PROTECTED:
            output.append(normalizer.normalize(t))
        else:
            output.append(t)
    return " ".join(output)

def clean_text(text):
      if text is None:
        return ""
      text = re.sub(r"http\S+|www\S+|@\w+|#", "", text)
      text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
      return text.lower().strip()