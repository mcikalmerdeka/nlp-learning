import pandas as pd
import numpy as np
max_seq_len = 100
d_model = 64
class NumPyEmbedding:
    def __init__(self, vocab_size, embedding_dim):
        self.weights = np.random.randn(vocab_size, embedding_dim) * 0.01  # Small random weights
        self.inputs = None
    def forward(self, inputs):
        self.inputs = np.asarray(inputs, dtype=np.int32)
        return self.weights[self.inputs]  # Look up embeddings
    def backward(self, d_output):
        d_weights = np.zeros_like(self.weights)
        np.add.at(d_weights, self.inputs, d_output)
        self.d_weights = d_weights
        return d_weights


class Embedding:
    def __init__(self, vocab_size, d_model, max_seq_len):
        self.token_embed = NumPyEmbedding(vocab_size, d_model)
        self.pe = self._positional_encoding(max_seq_len, d_model)
    def _positional_encoding(self, max_seq_len, d_model):
        pe = np.zeros((max_seq_len, d_model))
        position = np.arange(max_seq_len)[:, np.newaxis]  # (100, 1)
        div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))
        pe[:, 0::2] = np.sin(position * div_term)   # even indices
        pe[:, 1::2] = np.cos(position * div_term)   # odd indices
        return pe
    def forward(self, x): #just the function to use all of em
        embedded = self.token_embed.forward(x)
        return embedded + self.pe[:x.shape[1]]