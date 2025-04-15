import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

# PostgreSQL connection
DATABASE_URL = "postgresql://postgres:Harsh%40123@localhost:5432/capstone.db"
engine = create_engine(DATABASE_URL)

# Load data from the 'materials' table
df = pd.read_sql("SELECT carbon_savings, actual_usage FROM materials", engine)

# Drop rows with missing values
df = df.dropna(subset=["carbon_savings", "actual_usage"])

# Prepare features and target
X = df[["carbon_savings"]]
y = df["actual_usage"]

# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print(f"Model trained. MSE: {mse:.2f}")

# Save model
joblib.dump(model, "ml_model.pkl")
print("✅ Model saved as ml_model.pkl")
