# 📦 predict_lstm.py — LSTM 예측 모델 학습 및 예측
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def prepare_data(df, seq_len=50):
    data = df["close"].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)

    X, y = [], []
    for i in range(seq_len, len(scaled)-1):
        X.append(scaled[i-seq_len:i])
        y.append(scaled[i+1])

    return np.array(X), np.array(y), scaler

def train_lstm(df):
    X, y, scaler = prepare_data(df)

    model = Sequential()
    model.add(LSTM(50, activation="relu", input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=10, batch_size=32, verbose=0)
    return model, scaler

def predict_future_lstm(model, scaler, df, seq_len=50):
    data = df["close"].values.reshape(-1, 1)
    scaled = scaler.transform(data)
    input_seq = scaled[-seq_len:].reshape(1, seq_len, 1)
    prediction = model.predict(input_seq)
    predicted_price = scaler.inverse_transform(prediction)[0][0]
    current_price = df["close"].iloc[-1]

    return predicted_price > current_price  # 상승 예상 여부

def train_lstm(df): ...
def predict_future_lstm(model, scaler, df): ...
def get_lstm_confidence(model, scaler, df): ...
