"""
Feature Importance
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

pipe = joblib.load("models/best_model.pkl")
model = pipe.named_steps["model"]
prep = pipe.named_steps["prep"]

cat_features = prep.named_transformers_["cat"].get_feature_names_out(["Area", "Item"])
num_features = ["Year", "rainfall", "pesticides", "temp"]
all_features = list(cat_features) + num_features

importances = model.feature_importances_
imp_df = pd.DataFrame({"feature": all_features, "importance": importances})
imp_df = imp_df.sort_values("importance", ascending=False)

# تجميع أهمية الـ Area والـ Item ككل (بدل ما تتفرق على كل قيمة)
area_importance = imp_df[imp_df["feature"].str.startswith("Area_")]["importance"].sum()
item_importance = imp_df[imp_df["feature"].str.startswith("Item_")]["importance"].sum()

grouped = pd.DataFrame({
    "feature": ["Area (grouped)", "Item (grouped)", "Year", "rainfall", "pesticides", "temp"],
    "importance": [
        area_importance, item_importance,
        imp_df.loc[imp_df.feature == "Year", "importance"].values[0],
        imp_df.loc[imp_df.feature == "rainfall", "importance"].values[0],
        imp_df.loc[imp_df.feature == "pesticides", "importance"].values[0],
        imp_df.loc[imp_df.feature == "temp", "importance"].values[0],
    ]
}).sort_values("importance", ascending=False)

print(grouped)

plt.figure(figsize=(8, 5))
plt.barh(grouped["feature"], grouped["importance"], color="seagreen")
plt.gca().invert_yaxis()
plt.title("Feature Importance (grouped)")
plt.xlabel("Importance")
plt.tight_layout()
plt.savefig("outputs/feature_importance.png", dpi=120)
print("\nتم حفظ outputs/feature_importance.png")
