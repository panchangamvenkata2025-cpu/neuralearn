import numpy as np
import shap
import lime.lime_tabular
from sklearn.ensemble import GradientBoostingClassifier


class LevelClassifier:
    def __init__(self):
        self.model = GradientBoostingClassifier()
        self._train()

    def _train(self):
        np.random.seed(42)

        X = np.random.rand(200, 3)
        y = np.where(X[:,0] > 0.6, 1, 0)  # simple binary

        self.model.fit(X, y)

        self.explainer = shap.Explainer(self.model, X)
        self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            X,
            feature_names=["accuracy", "time", "hints"],
            class_names=["beginner", "advanced"]
        )

    def explain(self, features):
        features = np.array(features).reshape(1, -1)

        shap_values = self.explainer(features)

        lime_exp = self.lime_explainer.explain_instance(
            features[0],
            self.model.predict_proba
        )

        return {
            "prediction": int(self.model.predict(features)[0]),
            "shap_values": shap_values.values.tolist(),
            "lime_explanation": lime_exp.as_list()
        }