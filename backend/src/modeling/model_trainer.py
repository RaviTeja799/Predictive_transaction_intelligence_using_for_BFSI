import pandas as pd
import json
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.impute import SimpleImputer
import pickle

class ModelTrainer:
    def __init__(self):
        self.train_path = Path("backend/data/processed/train.csv")
        self.val_path = Path("backend/data/processed/validation.csv")
        self.test_path = Path("backend/data/processed/test.csv")
        self.output_dir = Path("backend/final_fraud_model")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self):
        train = pd.read_csv(self.train_path)
        val = pd.read_csv(self.val_path)
        test = pd.read_csv(self.test_path)
        print(f"✅ Loaded datasets: Train={train.shape}, Val={val.shape}, Test={test.shape}")
        return train, val, test

    def preprocess(self, df):
        #Drop unused columns
        X = df.drop(columns=['is_fraud','transaction_id','customer_id','timestamp'])
        y = df['is_fraud']
        #Handle missing values
        imputer = SimpleImputer(strategy="median")
        X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
        return X_imputed, y

    def save_features(self, X_train):
        with open(self.output_dir / "features.pkl", "wb") as f:
            pickle.dump(X_train.columns.tolist(), f)
        print(f"✅ Feature list saved at {self.output_dir / 'features.pkl'}")

    def scale_data(self, X_train, X_val, X_test):
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        #Save scaler
        with open(self.output_dir / "scaler.pkl", "wb") as f:
            pickle.dump(scaler, f)
        print(f"✅ Scaler saved at {self.output_dir / 'scaler.pkl'}")
        return X_train_scaled, X_val_scaled, X_test_scaled

    def evaluate(self, model, X, y):
        y_pred = model.predict(X)
        y_prob = model.predict_proba(X)[:, 1]
        return {
            "accuracy": round(accuracy_score(y, y_pred), 4),
            "precision": round(precision_score(y, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y, y_pred, zero_division=0), 4),
            "f1_score": round(f1_score(y, y_pred, zero_division=0), 4),
            "roc_auc": round(roc_auc_score(y, y_prob), 4)
        }

    def train_all_models(self):
        train_df, val_df, test_df = self.load_data()
        X_train, y_train = self.preprocess(train_df)
        X_val, y_val = self.preprocess(val_df)
        X_test, y_test = self.preprocess(test_df)

        #Save features before scaling
        self.save_features(X_train)

        X_train, X_val, X_test = self.scale_data(X_train, X_val, X_test)

        models = {
            "LogisticRegression": LogisticRegression(max_iter=2000, random_state=42),
            "RandomForest": RandomForestClassifier(n_estimators=150, random_state=42),
            "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42),
            "LightGBM": LGBMClassifier(random_state=42)
        }

        results = {}
        for name, model in models.items():
            print(f"🔹 Training {name}...")
            model.fit(X_train, y_train)
            val_metrics = self.evaluate(model, X_val, y_val)
            test_metrics = self.evaluate(model, X_test, y_test)
            results[name] = {"validation": val_metrics, "test": test_metrics}
            #Save each model as .pkl
            with open(self.output_dir / f"{name.lower()}_model.pkl", "wb") as f:
                pickle.dump(model, f)

        #best model by validation ROC-AUC
        best_model_name = max(results, key=lambda k: results[k]["validation"]["roc_auc"])
        best_model_auc = results[best_model_name]["validation"]["roc_auc"]
        with open(self.output_dir / "best_model.pkl", "wb") as f:
            pickle.dump(models[best_model_name], f)

        #metrics
        with open(self.output_dir / "model_comparison.json", "w") as f:
            json.dump(results, f, indent=4)

        print("\n✅ All models trained and saved as .pkl!")
        print(f"📊 Metrics stored at {self.output_dir / 'model_comparison.json'}")
        print(f"🏆 Best Model: {best_model_name} (ROC-AUC={best_model_auc})")

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train_all_models()
