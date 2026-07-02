import pandas as pd 
import numpy as np

from attention import Attention
from ffn import FeedForward
from layernorm import LayerNorm as ln
class TransformerBlock:
    def __init__(self, d_model, num_heads, d_ff, max_seq_len):
        self.attention = Attention(d_model, num_heads, max_seq_len)
        self.ffn = FeedForward(d_model, d_ff)
        self.ln1 = ln(d_model)
        self.ln2 = ln(d_model) #two separate gammas and betas
        

    def forward(self, x, token_ids):
        attn_output = self.attention.forward(x, token_ids)
        x = x + attn_output # Residual
        x = self.ln1.forward(x)


        ffn_output = self.ffn.forward(x)
        x = x + ffn_output # Residual
        x = self.ln2.forward(x)
        return x
    def backward(self, d_out):
        # Reverse order of forward
        
        # 4. LayerNorm 2 backward
        d_x = self.ln2.backward(d_out)
        
        # 3. FFN + residual
        d_ffn = self.ffn.backward(d_x)
        d_x = d_x + d_ffn  # residual: gradients ADD
        
        # 2. LayerNorm 1 backward
        d_x = self.ln1.backward(d_x)
        
        # 1. Attention + residual
        d_attn = self.attention.backward(d_x)
        d_x = d_x + d_attn  # residual: gradients ADD
        
        return d_x

class Transformer:
    def __init__(self, d_model, num_heads, d_ff, max_seq_len, num_blocks, vocab_size=28):
        self.blocks = [TransformerBlock(d_model, num_heads, d_ff, max_seq_len) for _ in range(num_blocks)]
        self.output_proj = np.random.randn(d_model, vocab_size) * 0.01
    def forward(self, x, token_ids):
        for block in self.blocks:
            x = block.forward(x, token_ids)
        self.x = x
        logits = x @ self.output_proj  # (batch, seq_len, vocab_size)
        return logits
    
    def backward(self, d_logits):
        # Gradient for output projection
        self.d_output_proj = np.tensordot(self.x, d_logits, axes=([0,1], [0,1]))
        
        # Gradient flowing into blocks
        d_x = d_logits @ self.output_proj.T
        
        # Backward through blocks in reverse
        for block in reversed(self.blocks):
            d_x = block.backward(d_x)
        
        return d_x