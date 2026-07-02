import pandas as pd 
import numpy as np

class EntropyLoss:
    def forward(self, logits, targets):
        # logits: (batch, seq_len, vocab_size)
        # targets: (batch, seq_len) — integer indices

        self.logits = logits
        self.targets = targets

        shifted = logits - np.max(logits, axis=-1, keepdims=True)
        exp_logits = np.exp(shifted)
        self.probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

        #Cross - entropy (one hot encoded)
        batch_size, seq_len = targets.shape
        self.batch_size = batch_size
        self.seq_len = seq_len

        loss = -np.log(self.probs[np.arange(batch_size)[:, None], np.arange(seq_len), targets]  + 1e-9)

        mask = (targets!=0) #boolean
        loss = loss * mask
        return np.sum(loss) / np.sum(mask)
    
    def backward(self):
        one_hot = np.zeros_like(self.probs)
        one_hot[np.arange(self.batch_size)[:, None], np.arange(self.seq_len), self.targets] = 1

        d_logits = self.probs - one_hot #back prop eq

        mask = (self.targets != 0)[:, :, np.newaxis]
        d_logits = d_logits * mask
        d_logits = d_logits / np.sum(mask)
        return d_logits