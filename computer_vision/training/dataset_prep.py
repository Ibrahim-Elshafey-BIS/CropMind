"""
Dataset Preparation — PlantVillage Balancing
الداتا: PlantVillage Dataset (23 Class)
الخطوة: Undersample الـ Classes فوق 1500
"""
import os, shutil, random

data_dir = "path/to/plantvillage/color"
output_dir = "path/to/balanced_dataset"
MAX = 1500

os.makedirs(output_dir, exist_ok=True)

for cls in os.listdir(data_dir):
    cls_path = os.path.join(data_dir, cls)
    if not os.path.isdir(cls_path):
        continue
    out_cls = os.path.join(output_dir, cls)
    os.makedirs(out_cls, exist_ok=True)
    images = os.listdir(cls_path)
    random.shuffle(images)
    selected = images[:min(MAX, len(images))]
    for img in selected:
        shutil.copy(os.path.join(cls_path, img), os.path.join(out_cls, img))
    print(f"{cls}: {len(selected)}")
