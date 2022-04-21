import fasttext
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from db.db_utils import get_descriptions


class ModelFastText:
    def __init__(self, db_path, model_path):
        self.model = fasttext.load_model(model_path)
        self.X = self.fit(db_path)

    def fit(self, db_path: str) -> np.array:
        X = []
        for description in get_descriptions(db_path=db_path):
            X.append(self.model.get_sentence_vector(description))
        return np.array(X)

    def predict(self, query: str) -> np.array:
        if self.X is None:
            return None
        query_vec = self.model.get_sentence_vector(query).reshape(1, -1)
        scores = np.apply_along_axis(lambda x: cosine_similarity(x.reshape(1, -1), query_vec)[0][0], 1, self.X)
        return scores
