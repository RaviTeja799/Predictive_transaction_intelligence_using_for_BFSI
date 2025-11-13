import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path

# 1️⃣ Load dataset
data_path = Path("backend/data/raw/transactions_clean.csv")
df = pd.read_csv(data_path)
print(f"✅ Loaded dataset with shape: {df.shape}")

# 2️⃣ First split: Train (70%) + Temp (30%)
train_df, temp_df = train_test_split(df, test_size=0.30, random_state=42, stratify=df["is_fraud"])

# 3️⃣ Second split: Validation (15%) + Test (15%)
val_df, test_df = train_test_split(temp_df, test_size=0.50, random_state=42, stratify=temp_df["is_fraud"])

# 4️⃣ Create output folders
processed_path = Path("backend/data/processed")
processed_path.mkdir(parents=True, exist_ok=True)

# 5️⃣ Save splits
train_df.to_csv(processed_path / "train.csv", index=False)
val_df.to_csv(processed_path / "validation.csv", index=False)
test_df.to_csv(processed_path / "test.csv", index=False)

print("✅ Data split completed:")
print(f"Train: {train_df.shape}, Validation: {val_df.shape}, Test: {test_df.shape}")
