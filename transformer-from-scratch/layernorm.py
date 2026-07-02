import pandas as pd 
import numpy as np
class LayerNorm:
    def __init__(self, d_model):
        self.d_model = d_model
        self.gamma = np.ones(d_model)
        self.beta = np.zeros(d_model)

    def forward(self, x):
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        self.var = var  
        x_norm = (x - mean) / np.sqrt(var + 1e-6)
        self.norm = x_norm
        return self.gamma * x_norm + self.beta
    def backward(self, d_out):
        d_gamma = np.sum(self.norm * d_out, axis=(0,1))
        d_beta = np.sum(d_out, axis=(0,1))
        self.d_gamma = d_gamma
        self.d_beta = d_beta
        d_x_norm = d_out * self.gamma
        d_x = (1.0 / np.sqrt(self.var + 1e-6)) * (
            d_x_norm
            - np.mean(d_x_norm, axis=-1, keepdims=True)
            - self.norm * np.mean(d_x_norm * self.norm, axis=-1, keepdims=True)
        )
        return d_x