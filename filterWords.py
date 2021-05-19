#import nltk; nltk.download('punkt')
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 

def filter(example_sent):
  stop_words = set(stopwords.words('english')) 
  word_tokens = word_tokenize(example_sent) 
  filtered_sentence = [w for w in word_tokens if not w in stop_words] 
  filtered_sentence = ""
  for w in word_tokens: 
    if w not in stop_words: 
        filtered_sentence +=w+' '
  if(filtered_sentence==''):
    filtered_sentence = example_sent
  else:
    filtered_sentence = filtered_sentence[:-1]
  return(filtered_sentence)
