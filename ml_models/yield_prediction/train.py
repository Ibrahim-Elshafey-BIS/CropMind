"""
تدريب موديل توقع الـ Crop Yield
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from xgboost import XGBRegressor
import joblib

df = pd.read_csv("data/yield_clean.csv")

X = df.drop(columns=["yield"])
y = df["yield"]

cat_cols = ["Area", "Item"]
num_cols = ["Year", "rainfall", "pesticides", "temp"]

preprocessor = ColumnTransformer(transformers=[
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ("num", StandardScaler(), num_cols)
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

def evaluate(name, model):
    pipe = Pipeline([("prep", preprocessor), ("model", model)])
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    print(f"\n{name}")
    print(f"  MAE  : {mae:,.0f}")
    print(f"  RMSE : {rmse:,.0f}")
    print(f"  R2   : {r2:.4f}")
    return pipe, r2

rf = RandomForestRegressor(n_estimators=300, max_depth=18, min_samples_leaf=2, random_state=42, n_jobs=-1)
xgb = XGBRegressor(n_estimators=400, max_depth=8, learning_rate=0.05, random_state=42, n_jobs=-1)

rf_pipe, rf_r2 = evaluate("Random Forest", rf)
xgb_pipe, xgb_r2 = evaluate("XGBoost", xgb)

best_pipe, best_name = (rf_pipe, "random_forest") if rf_r2 > xgb_r2 else (xgb_pipe, "xgboost")
print(f"\n>> أفضل موديل: {best_name}")

joblib.dump(best_pipe, "models/best_model.pkl", compress=3)
print("تم حفظ الموديل في models/best_model.pkl")
