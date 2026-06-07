import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

data = {
    "description": [
        "swiggy order",
        "zomato delivery",
        "pizza hut",
        "burger king",
        "coffee shop",
        "restaurant bill",

        "uber ride",
        "ola cab",
        "bus ticket",
        "train ticket",
        "petrol pump",

        "amazon purchase",
        "flipkart order",
        "myntra shopping",
        "ajio purchase",

        "movie ticket",
        "netflix subscription",
        "spotify premium",
        "hotstar subscription"
    ],

    "category": [
        "Food","Food","Food","Food","Food","Food",
        "Travel","Travel","Travel","Travel","Travel",
        "Shopping","Shopping","Shopping","Shopping",
        "Entertainment","Entertainment","Entertainment","Entertainment"
    ]
}

df = pd.DataFrame(data)

model = Pipeline([
    ("vectorizer", CountVectorizer()),
    ("classifier", MultinomialNB())
])

model.fit(
    df["description"],
    df["category"]
)

joblib.dump(
    model,
    "expense_model.pkl"
)

print("Model Trained Successfully")