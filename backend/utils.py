# This prevents over normalization for english words if they are not likely to be singlish and also preserves the case for proper nouns and named entities.
import re

ENGLISH_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "is", "are", "was", "were", "be", "been"
}

def tokenize(text):
  return text.split()

def looks_like_singlish(token):
    token = token.lower()
    # Common markers that don't usually appear in English words
    markers = ["aa", "ee", "oo", "uu", "nnd", "nng", "nd", "mko", "khmd"]
    return any(m in token for m in markers)

def selective_singlish_normalize(text,normalizer):
  tokens = tokenize(text)
  output = []

  for t in tokens:
    t_lower = t.lower()

    if t.isdigit() or t_lower in ENGLISH_STOPWORDS:
      output.append(t)
      continue

    
    if t[0].isupper() and not looks_like_singlish(t):
      output.append(t)
      continue
    
    if looks_like_singlish(t):
      normed = normalizer.normalize(t)

      if isinstance(normed,tuple):
        normed = normed[0]
        output.append(normed)
    else:
      output.append(t)

  return " ".join(output)

def clean_text(text):
  if not isinstance(text,str):
    return ""
  text = re.sub(r"http\S+|www\S+","",text)
  text = re.sub(r"@\w+","",text)
  text = re.sub(r"\s+"," ",text).strip()
  return text

    