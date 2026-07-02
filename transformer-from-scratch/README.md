# Transformer from Scratch — NumPy Only

A fully from-scratch implementation of a GPT-style transformer with multi-head self-attention, positional encodings, feed-forward networks, and layer normalization. Trained on next-character prediction using 1,000 random English sentences. Every component — attention, backpropagation, loss, and generation — built with NumPy. No PyTorch. No TensorFlow.

## Project Structure

```
├── train.py                  # Training loop + text generation
├── test_forward.py           # Forward pass test on sample data
├── data.py                   # Data preprocessing and padding
├── block.py                  # Transformer block + full Transformer
├── attention.py              # Multi-head causal self-attention
├── embedding.py              # Token embeddings + positional encoding
├── ffn.py                    # Feed-forward network (ReLU)
├── layernorm.py              # Layer normalization
├── loss.py                   # Cross-entropy loss
├── Random English Sentences.txt  # Training data (1,000 sentences)
├── randdata.csv              # Same data with column header
└── README.md
```

## Architecture

### Transformer Block

```
Input → Attention → + Residual → LayerNorm → FFN → + Residual → LayerNorm → Output
```

### Multi-Head Causal Self-Attention

```
Input → Q, K, V projections → Split into heads → 
Scaled dot-product attention with causal mask + pad mask → 
Concatenate heads → Output projection
```

### Token Embedding + Positional Encoding

Words are mapped to 64-dimensional vectors. Sinusoidal positional encodings are added to give the model position awareness without learned parameters.

### Model Specs

| Parameter | Value |
|-----------|-------|
| d_model | 64 |
| num_heads | 4 |
| d_ff | 256 |
| num_blocks | 2 |
| vocab_size | 28 (a-z + space + pad) |
| max_seq_len | 100 |
| Parameters | ~100K |

## Training

The model is trained on next-character prediction with cross-entropy loss. Given a sequence of characters, it predicts the next character at each position. A causal mask prevents attending to future tokens.

```python
# Target: shift input right by one
targets[:, :-1] = token_ids[:, 1:]
# "hello" → predict "e", "l", "l", "o"
```

Gradient descent updates all weights manually — no autograd. Each component stores its own gradients computed during the backward pass.

## How It Works

### Forward Pass

1. **Embedding**: Token IDs → 64-dim vectors + positional encoding
2. **Transformer Blocks (×2)**: Self-attention → FFN → LayerNorm with residuals
3. **Output Projection**: 64-dim → 28-dim logits (one per vocabulary token)

### Backward Pass

Gradients flow in reverse:
1. Cross-entropy loss backward → d_logits
2. Output projection backward → d_x
3. Each transformer block backward (reverse order):
   - LayerNorm2 → FFN + residual → LayerNorm1 → Attention + residual
4. Attention backward: d_Q, d_K, d_V → weight gradients
5. Embedding backward: accumulate gradients into embedding table

### Generation

Autoregressive sampling: start with a single character, repeatedly predict the next token, append it, and feed the growing sequence back into the model.

## Results

After many training loops on 1,000 sentences, the model generates character sequences that resemble English words and phrases — not coherent sentences, but clear patterns of letter frequencies and common letter combinations emerge from the data.

## What I Learned

- **Backprop through attention**: The softmax gradient requires computing `s * (d_weights - sum(d_weights * s))`. Getting the shapes right across batch, heads, and sequence dimensions was the hardest part.
- **Residual connections add gradients**: In backward, `d_x = d_x + d_attn` — the gradient flows through BOTH the skip connection and the attention path.
- **Causal + pad mask**: Both masks must be applied before softmax, then the masked positions must also be zeroed in the backward pass to prevent gradient flow through padding.
- **LayerNorm backward**: The full derivative has three terms — the direct gradient, minus the mean, minus a covariance correction. Easy to get wrong.
- **NumPy embedding backward**: `np.add.at` is essential for accumulating gradients when multiple input positions reference the same embedding row.

## Usage

```bash
python train.py
```

Trains for 200 epochs and prints generated text after each epoch.

## Dependencies

```bash
pip install numpy pandas
```

## Why This Matters

This is the same architecture behind GPT, scaled down. Understanding every gradient, every shape transformation, every mask — that's the foundation for working with any transformer model. No magic. Just matrix multiplication and backpropagation.
