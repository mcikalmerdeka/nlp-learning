import pandas as pd 
import numpy as np 

from block import Transformer
from embedding import Embedding

loops = 200

def sentence_to_vector(sentence):
    vec = []
    for char in sentence.lower():
        if char.isalpha():
            vec.append(ord(char) - ord('a') + 1)   # a=1 through z=26
        elif char == ' ':
            vec.append(27)                          # space = 27
    return vec

with open('Random English Sentences.txt', 'r') as f:
    sentences = [line.strip() for line in f if line.strip()]

vectors = [sentence_to_vector(s) for s in sentences]

max_length = 100

padded = []
for vec in vectors:
    if len(vec) > max_length:
        padded.append(vec[:max_length])
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

print(f'Embedded shape: {x.shape}')

model = Transformer(d_model, num_heads, d_ff, max_length, num_blocks, vocab_size)
logits = model.forward(x, token_ids)

print(f'Logits shape: {logits.shape}')

targets = np.zeros_like(token_ids)
targets[:, :-1] = token_ids[:, 1:]
targets[:, -1] = 0

from loss import EntropyLoss

for i in range(loops):
    x = embedding.forward(token_ids)
    logits = model.forward(x, token_ids)
    
    loss_fn = EntropyLoss()
    loss = loss_fn.forward(logits, targets)
    d_logits = loss_fn.backward()
    
    d_x = model.backward(d_logits)
    embedding.token_embed.backward(d_x)

    lr = 0.001

    # Output projection
    model.output_proj -= lr * model.d_output_proj

    # Each block
    for block in model.blocks:
        # Attention
        block.attention.W_q -= lr * block.attention.d_W_q
        block.attention.W_k -= lr * block.attention.d_W_k
        block.attention.W_v -= lr * block.attention.d_W_v
        block.attention.W_o -= lr * block.attention.d_W_o
        
        # FFN
        block.ffn.W1 -= lr * block.ffn.d_W1
        block.ffn.b1 -= lr * block.ffn.d_b1
        block.ffn.W2 -= lr * block.ffn.d_W2
        block.ffn.b2 -= lr * block.ffn.d_b2
        
        # LayerNorms
        block.ln1.gamma -= lr * block.ln1.d_gamma
        block.ln1.beta -= lr * block.ln1.d_beta
        block.ln2.gamma -= lr * block.ln2.d_gamma
        block.ln2.beta -= lr * block.ln2.d_beta

    # Embedding
    embedding.token_embed.weights -= lr * embedding.token_embed.d_weights

    print(f"Epoch {i+1}/{loops} - Loss: {loss:.4f}")

# Generation (outside training loop)
idx_to_char = {0: '[PAD]'}
for i in range(1, 27):
    idx_to_char[i] = chr(ord('a') + i - 1)
idx_to_char[27] = ' '

generated = [1]  # start with 'a'

for _ in range(100):
    seq = generated + [0] * (max_length - len(generated))
    seq = np.array([seq])
    
    x = embedding.forward(seq)
    logits = model.forward(x, seq)
    
    last_pos = len(generated) - 1
    probs = np.exp(logits[0, last_pos] - np.max(logits[0, last_pos]))
    probs = probs / np.sum(probs)
    probs[0] = 0  # block PAD
    probs = probs / np.sum(probs)
    
    next_token = np.random.choice(28, p=probs)
    generated.append(next_token)

chars = [idx_to_char[t] for t in generated]
print("\nGenerated text:")
print(''.join(chars))