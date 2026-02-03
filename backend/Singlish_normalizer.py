import re

class ProfessionalNormalizer:
    def __init__(self):
        # Define common professional titles and their normalized forms
        self.dictionary = {
            "mko":"මොකද", "bn":"බං", "bro":"බ්‍රෝ", "sis":"සිස්",
            "khmd":"කොහොමද", "dnt":"දන්නෙ නැ", "plz":"පීල්ස්",
            "api":"අපි", "oyala":"ඔයාලා", "innwa":  "ඉන්නවා"

        }

        self.rules = [
            ('nnd', 'ඳ'), ('nng', 'ඟ'), ('nd', 'ඳ'),
            ('th', 'ත'), ('dh', 'ද'), ('sh', 'ෂ'), ('ch', 'ච'),
            ('aa', 'ආ'), ('ee', 'ඊ'), ('uu', 'ඌ'), ('oo', 'ඕ'),
            ('k', 'ක'), ('g', 'ග'), ('t', 'ට'), ('d', 'ද'),
            ('n', 'න'), ('p', 'ප'), ('b', 'බ'), ('m', 'ම'),
            ('y', 'ය'), ('r', 'ර'), ('l', 'ල'), ('w', 'ව'),
            ('s', 'ස'), ('h', 'හ'), ('a', 'අ'), ('i', 'ඉ'),
            ('u', 'උ'), ('e', 'එ'), ('o', 'ඔ') 
        ]
    
    def normalize(self, text: str)-> str:
        text = text.lower().strip()

        words = text.split()

        text = ' '.join([self.dictionary.get(word, word) for word in words])

        if re.search('[a-z]', text):
            for latin, sinhala in self.rules:
                text = text.replace(latin, sinhala)

       
        return text