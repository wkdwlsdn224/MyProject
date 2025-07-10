import pickle
import pandas as pd

def train_model():
    # 데이터 로드 → 전처리 → 모델 학습 → 저장
    df = pd.read_csv("training_data.csv")
    # ... 전처리, 학습 로직 ...
    model = ...  # 학습된 모델
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

def get_model_info() -> dict:
    # 예시로 메타 정보 반환
    return {"version": "1.0.0", "last_trained": "2025-07-01", "val_auc": 0.82}
