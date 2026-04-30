import numpy as np
import torch
from models.lstm_model import TrafficLSTM, make_sequences

def test_lstm_forward():
    model = TrafficLSTM(input_size=6, n_lanes=4)
    x = torch.randn(8, 12, 6)   # batch=8, seq=12, features=6
    out = model(x)
    assert out.shape == (8, 4)

def test_make_sequences():
    data = np.random.rand(100, 6).astype("float32")
    X, y = make_sequences(data, seq_len=12)
    assert X.shape == (88, 12, 6)
    assert y.shape[0] == 88

def test_lstm_output_range():
    model = TrafficLSTM(input_size=6, n_lanes=4)
    x = torch.zeros(1, 12, 6)
    out = model(x)
    # Output should be finite
    assert torch.isfinite(out).all()
