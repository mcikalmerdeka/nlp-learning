import pandas as pd 
import numpy as np

from block import Transformer
from embedding import Embedding

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

token_ids = np.array(padded)


d_model = 64
num_heads = 4
d_ff = 256
num_blocks = 2
vocab_size = 28
batch_size = token_ids.shape[0]


embedding = Embedding(vocab_size, d_model, max_length)
x = embedding.forward(token_ids)

print(f'Embedded shape:', x.shape)

model = Transformer(d_model, num_heads, d_ff, max_length, num_blocks, vocab_size)
logits = model.forward(x, token_ids)

print(f'Logits shape: {logits.shape}')

#probs:
probs = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
probs = probs / np.sum(probs, axis=-1, keepdims=True)
prediction = np.argmax(probs, axis=-1)

idx_to_char = {0: '[PAD]'}
for i in range(1, 27):
    idx_to_char[i] = chr(ord('a') + i - 1)  # 1→a, 2→b, ..., 26→z
idx_to_char[27] = ' '                        # 27→space


print("\nFirst sentence predictions:")
chars = [idx_to_char[p] for p in prediction[0][:50]]
print(''.join(chars))