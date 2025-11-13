from src.preprocessing.data_loader import DataLoader

path = "backend/data/raw/transactions_clean.csv"
loader = DataLoader(path)
df = loader.load_data()
print("Shape:", df.shape)
print("Columns:", df.columns[:10])
