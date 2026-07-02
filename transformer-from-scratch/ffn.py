import numpy as np
import pandas as pd
class FeedForward:
    def __init__(self, d_model, d_ff):
        self.d_model = d_model
        self.d_ff = d_ff
        
        self.W1 = np.random.randn(d_model, d_ff) * 0.01
        self.b1 = np.zeros(d_ff)
        self.W2 = np.random.randn(d_ff, d_model) * 0.01
        self.b2 = np.zeros(d_model)
    def forward(self, x):
        self.x = x
        z1 = np.dot(x, self.W1) + self.b1
        self.z1 = z1
        a1 = np.maximum(0, z1)  # ReLU activation
        self.a1 = a1
        z2 = np.dot(a1, self.W2) + self.b2
        return z2
    def backward(self, d_out):
        d_W2 = np.tensordot(self.a1, d_out, axes=([0,1], [0,1]))  # (d_ff, d_model)
        d_b2 = np.sum(d_out, axis=(0,1))     
        d_a1 = d_out @ self.W2.T
        d_z1 = d_a1 * (self.z1 > 0) #relu backwards
        d_W1 = np.tensordot(self.x, d_z1, axes=([0,1], [0,1]))   # (d_model, d_ff)
        d_b1 = np.sum(d_z1, axis=(0,1))    
        d_x = d_z1 @ self.W1.T
        self.d_W1 = d_W1
        self.d_b1 = d_b1
        self.d_W2 = d_W2
        self.d_b2 = d_b2
        return d_x