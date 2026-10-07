import os

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SchemeSetuEngine:
    def __init__(self, data_path="schemes.csv"):
        if not os.path.exists(data_path):
            raise FileNotFoundError(
                "schemes.csv not found. Run preprocess.py first."
            )

        self.df = pd.read_csv(data_path)

        self.df["clean_description"] = (
            self.df["clean_description"]
            .fillna("")
            .astype(str)
        )

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=50000,
        )

        self.matrix = self.vectorizer.fit_transform(
            self.df["clean_description"]
        )

    def _profile_text(self, profile):
        if not profile:
            return ""

        useful_fields = [
            "applicant_type",
            "gender",
            "state",
            "district",
            "area_type",
            "social_category",
            "occupation",
            "bpl_status",
            "marital_status",
            "minority_status",
            "education_level",
            "course",
            "study_year",
            "institution_type",
            "has_disability",
            "is_farmer",
            "farmer_type",
            "business_type",
        ]

        parts = []

        for field in useful_fields:
            value = profile.get(field)

            if value not in (None, "", "No"):
                parts.append(str(value))

        age = profile.get("age")
        income = profile.get("annual_income")

        if age is not None:
            parts.append(f"age {age}")

        if income is not None:
            parts.append(f"family income {income}")

        return " ".join(parts)

    def recommend(self, user_query, profile=None, top_k=10):
        profile_text = self._profile_text(profile)

        combined_query = " ".join(
            part
            for part in [user_query, profile_text]
            if part
        )

        if not combined_query.strip():
            return pd.DataFrame()

        query_vector = self.vectorizer.transform(
            [combined_query]
        )

        scores = cosine_similarity(
            query_vector,
            self.matrix,
        ).flatten()

        results = self.df.copy()
        results["match_score"] = (scores * 100).round(2)

        results = results.sort_values(
            "match_score",
            ascending=False,
        )

        columns = [
            "name",
            "match_score",
            "level",
            "schemeCategory",
            "eligibility",
            "benefits",
            "documents",
            "application",
        ]

        columns = [
            col for col in columns
            if col in results.columns
        ]

        return results.head(top_k)[columns]
