from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from db.db_utils import get_descriptions


class ModelTfIdf:
    def __init__(self, db_path):
        self.model = TfidfVectorizer()
        self.X = self.fit(get_descriptions(db_path=db_path))

    def fit(self, data) -> np.array:
        return self.model.fit_transform(data).toarray()

    def predict(self, query: str):
        if self.X is None:
            return None
        query_vec = self.model.transform([query]).toarray().reshape(1, -1)
        scores = np.apply_along_axis(lambda x: cosine_similarity(x.reshape(1, -1), query_vec)[0][0], 1, self.X)
        return scores
