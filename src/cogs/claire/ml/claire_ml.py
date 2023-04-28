import numpy as np
import pandas as pd

from typing import List
from database.guild import db

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class ClaireSpam:
    def __init__(self):
        self.df = pd.DataFrame.from_dict(get_queries())
        X = self.df.details
        y = self.df.label
        X_train, X_test, y_train, y_test = self.get_split(X, y)

        model = Pipeline(
            [
                ('vect', CountVectorizer(token_pattern=r"(?u)\b\w+\b|[^\s]")),
                ('clf', LogisticRegression())
            ]
        )

        model.fit(X_train, y_train)
        self.model = model
        predicted_labels = model.predict(X_test)
        accuracy = accuracy_score(y_test, predicted_labels)
        print(f"Spam filter complete with an Accuracy of {accuracy}")

    def get_split(self, X, y):
        clean_x = np.array([x if x else '' for x in X])
        return train_test_split(
            clean_x, y,
            train_size=.65,
            random_state=328
        )
    
    def predict(self, details: str):
        deets = np.array([details if details else ''])
        return self.model.predict(deets)[0]
    
    def probability_of_spam(self, details: str):
        deets = np.array([details if details else ''])
        probs = self.model.predict_proba(deets)
        return round(list(probs[0])[1], 3)


def insert_query(query: dict) -> bool:
    response = db.ClaireML.insert_one(query)
    return response.acknowledged

def insert_queries(queries: List[dict]) -> bool:
    response = db.ClaireML.insert_many(queries)
    return response.acknowledged

def delete_query(query: dict) -> bool:
    response = db.ClaireML.delete_one(query)
    return response.acknowledged

def get_queries() -> List[dict]:
    return db.ClaireML.find({})

def unique() -> List[dict]:
    unique = []
    unique_names = []
    qs = get_queries()
    for q in qs:
        if q['name'] not in unique_names:
            unique_names.append(q['name'])
            unique.append(
                {
                    'name': q['name'],
                    'details': q['details'],
                    'label': q['label']
                }
            )
    
    return unique

# def nuke_it():
#     for q in get_queries():
#         db.ClaireML.delete_one(q)