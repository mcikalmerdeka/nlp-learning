import pandas as pd 
import numpy as np

class Attention:
    def __init__(self, d_model, num_heads=4, max_seq_len=100):
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.max_seq_len = max_seq_len
        
        self.W_q = np.random.randn(d_model, d_model) * 0.01
        self.W_k = np.random.randn(d_model, d_model) * 0.01
        self.W_v = np.random.randn(d_model, d_model) * 0.01
        self.W_o = np.random.randn(d_model, d_model) * 0.01
        
        # Causal mask
        self.causal_mask = np.triu(np.ones((max_seq_len, max_seq_len)) * -np.inf, k=1)
    
    def forward(self, x, token_ids):
        # token_ids shape: (batch, seq_len)
        
        # MAKE THE PAD MASK RIGHT HERE
        pad_mask = (token_ids != 0)  # (batch, seq_len), True = real token
        
        batch_size, seq_len, _ = x.shape
        
        Q = x @ self.W_q
        K = x @ self.W_k
        V = x @ self.W_v
        
        self.x = x

        Q = Q.reshape(batch_size, seq_len, self.num_heads, self.d_k)
        K = K.reshape(batch_size, seq_len, self.num_heads, self.d_k)
        V = V.reshape(batch_size, seq_len, self.num_heads, self.d_k)
        
        
        Q = Q.transpose(0, 2, 1, 3)
        K = K.transpose(0, 2, 1, 3)
        V = V.transpose(0, 2, 1, 3)
        self.Q_heads = Q
        self.K_heads = K
        self.V_heads = V
        
        attn_output = self._scaled_dot_product_attention(Q, K, V, pad_mask)
        
        attn_output = attn_output.transpose(0, 2, 1, 3)
        attn_output = attn_output.reshape(batch_size, seq_len, self.d_model)
        self.concat_output = attn_output
        return attn_output @ self.W_o
    
    def _scaled_dot_product_attention(self, Q, K, V, pad_mask):
        d_k = Q.shape[-1]
        scores = Q @ K.transpose(0, 1, 3, 2) / np.sqrt(d_k)
        
        # Causal mask
        scores = scores + self.causal_mask[:scores.shape[-2], :scores.shape[-1]]
        
        # Pad mask
        pad_mask = pad_mask[:, np.newaxis, np.newaxis, :]  # (batch, 1, 1, seq_len)
        scores = np.where(pad_mask, scores, -np.inf)
        
        attn_weights = self.softmax(scores)
        self.scores = scores
        self.attn_weights = attn_weights
        self.pad_mask_expanded = pad_mask
        return attn_weights @ V
    
    def softmax(self, X):
        X = X - np.max(X, axis=-1, keepdims=True)
        X = np.exp(X)
        return X / np.sum(X, axis=-1, keepdims=True)
    def backward(self, d_out):
        d_concat = d_out @ self.W_o.T
        d_attn_heads = d_concat.reshape(d_out.shape[0], d_out.shape[1], self.num_heads, self.d_k).transpose(0, 2, 1, 3)
        d_W_o = np.tensordot(self.concat_output, d_out, axes=([0,1], [0,1]))
        self.d_W_o = d_W_o
        d_attn_weights = d_attn_heads @ self.V_heads.transpose(0, 1, 3, 2)
        d_V_heads = self.attn_weights.transpose(0, 1, 3, 2) @ d_attn_heads
        attn = self.attn_weights
        d_scores = attn * (d_attn_weights - np.sum(d_attn_weights * attn, axis=-1, keepdims=True))
        causal = (self.causal_mask[:d_scores.shape[-2], :d_scores.shape[-1]] == 0)
        d_scores = np.where(self.pad_mask_expanded & causal, d_scores, 0)
        d_Q_heads = d_scores @ self.K_heads / np.sqrt(self.d_k)
        d_K_heads = d_scores.transpose(0, 1, 3, 2) @ self.Q_heads / np.sqrt(self.d_k)
        d_Q = d_Q_heads.transpose(0, 2, 1, 3).reshape(d_out.shape[0], d_out.shape[1], self.d_model)
        d_K = d_K_heads.transpose(0, 2, 1, 3).reshape(d_out.shape[0], d_out.shape[1], self.d_model)
        d_V = d_V_heads.transpose(0, 2, 1, 3).reshape(d_out.shape[0], d_out.shape[1], self.d_model)

        self.d_W_q = np.tensordot(self.x, d_Q, axes=([0,1], [0,1]))
        self.d_W_k = np.tensordot(self.x, d_K, axes=([0,1], [0,1]))
        self.d_W_v = np.tensordot(self.x, d_V, axes=([0,1], [0,1]))

        d_x = d_Q @ self.W_q.T + d_K @ self.W_k.T + d_V @ self.W_v.T
        return d_x