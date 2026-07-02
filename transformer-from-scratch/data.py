import pandas as pd 
import numpy as np 

df = pd.read_csv('randdata.csv')

def sentence_to_vector(sentence):
    vec = []
    for char in sentence.lower():
        if char.isalpha():
            vec.append(ord(char) - ord('a') + 1)   # a=1 through z=26
        elif char == ' ':
            vec.append(27)                          # space = 27
    return vec

vectors = [sentence_to_vector(sentence) for sentence in df['sentence']]

max_length = 100

padded = []
for vec in vectors:
    if len(vec) > max_length:
        padded.append(vec[:max_length])  # Truncate if too long
    else:
        padded.append(vec + [0] * (max_length - len(vec)))

data = np.array(padded)
print(data.shape)