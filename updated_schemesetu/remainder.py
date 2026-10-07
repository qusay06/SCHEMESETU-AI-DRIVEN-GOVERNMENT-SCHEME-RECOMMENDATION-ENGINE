import os
import re
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------
# INDIA STATES + UNION TERRITORIES
# ---------------------------------------------------

STATE_ALIASES = {
    "andhra pradesh": [
        "andhra pradesh",
        "ap"
    ],

    "arunachal pradesh": [
        "arunachal pradesh"
    ],

    "assam": [
        "assam"
    ],

    "bihar": [
        "bihar"
    ],

    "chhattisgarh": [
        "chhattisgarh"
    ],

    "goa": [
        "goa"
    ],

    "gujarat": [
        "gujarat"
    ],

    "haryana": [
        "haryana"
    ],

    "himachal pradesh": [
        "himachal pradesh"
    ],

    "jharkhand": [
        "jharkhand"
    ],

    "karnataka": [
        "karnataka"
    ],

    "kerala": [
        "kerala"
    ],

    "madhya pradesh": [
        "madhya pradesh",
        "mp"
    ],

    "maharashtra": [
        "maharashtra"
    ],

    "manipur": [
        "manipur"
    ],

    "meghalaya": [
        "meghalaya"
    ],

    "mizoram": [
        "mizoram"
    ],

    "nagaland": [
        "nagaland"
    ],

    "odisha": [
        "odisha",
        "orissa"
    ],

    "punjab": [
        "punjab"
    ],

    "rajasthan": [
        "rajasthan"
    ],

    "sikkim": [
        "sikkim"
    ],

    "tamil nadu": [
        "tamil nadu",
        "tamilnadu"
    ],

    "telangana": [
        "telangana"
    ],

    "tripura": [
        "tripura"
    ],

    "uttar pradesh": [
        "uttar pradesh",
        "up"
    ],

    "uttarakhand": [
        "uttarakhand",
        "uttaranchal"
    ],

    "west bengal": [
        "west bengal"
    ],

    "andaman and nicobar islands": [
        "andaman and nicobar",
        "andaman nicobar"
    ],

    "chandigarh": [
        "chandigarh"
    ],

    "dadra and nagar haveli and daman and diu": [
        "dadra and nagar haveli",
        "daman and diu"
    ],

    "delhi": [
        "delhi",
        "nct delhi",
        "new delhi"
    ],

    "jammu and kashmir": [
        "jammu and kashmir",
        "jammu & kashmir"
    ],

    "ladakh": [
        "ladakh"
    ],

    "lakshadweep": [
        "lakshadweep"
    ],

    "puducherry": [
        "puducherry",
        "pondicherry"
    ],
}


# ---------------------------------------------------
# NORMALIZE TEXT
# ---------------------------------------------------

def normalize_text(value):

    if pd.isna(value):
        return ""

    value = str(value).lower()

    value = re.sub(
        r"[^a-z0-9\s&]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# ---------------------------------------------------
# NORMALIZE USER STATE
# ---------------------------------------------------

def normalize_state(user_state):

    state = normalize_text(user_state)

    for standard_state, aliases in STATE_ALIASES.items():

        if state == standard_state:
            return standard_state

        for alias in aliases:

            if state == alias:
                return standard_state

    return state


# ---------------------------------------------------
# FIND STATES MENTIONED IN SCHEME
# ---------------------------------------------------

def find_states_in_text(text):

    text = normalize_text(text)

    detected_states = set()

    for standard_state, aliases in STATE_ALIASES.items():

        for alias in aliases:

            # Avoid false matches for tiny aliases like UP / MP
            if len(alias) <= 2:
                continue

            pattern = (
                r"\b"
                + re.escape(alias)
                + r"\b"
            )

            if re.search(pattern, text):
                detected_states.add(
                    standard_state
                )

                break

    return detected_states


# ---------------------------------------------------
# STATE ELIGIBILITY CHECK
# ---------------------------------------------------

def check_state_eligibility(row, user_state):

    if not user_state:
        return True

    user_state = normalize_state(
        user_state
    )

    searchable_text = " ".join(
        [
            str(row.get("name", "")),
            str(row.get("eligibility", "")),
            str(row.get("details", "")),
            str(row.get("description", "")),
        ]
    )

    detected_states = find_states_in_text(
        searchable_text
    )

    # No state mentioned:
    # don't reject because it may be a Central scheme.
    if not detected_states:
        return True

    # User's state is explicitly mentioned.
    if user_state in detected_states:
        return True

    # Some other state is explicitly mentioned.
    # Example:
    # User = Tamil Nadu
    # Scheme = Madhya Pradesh residents only
    return False


# ---------------------------------------------------
# RECOMMENDATION ENGINE
# ---------------------------------------------------

class SchemeSetuEngine:

    def __init__(
        self,
        data_path="schemes.csv"
    ):

        if not os.path.exists(
            data_path
        ):

            raise FileNotFoundError(
                "schemes.csv not found. "
                "Run preprocess.py first."
            )

        self.df = pd.read_csv(
            data_path
        )

        # Make sure important columns exist
        required_columns = [
            "name",
            "clean_description",
            "eligibility",
            "benefits",
            "documents",
            "application",
            "details",
            "level",
            "schemeCategory",
        ]

        for column in required_columns:

            if column not in self.df.columns:
                self.df[column] = ""

            self.df[column] = (
                self.df[column]
                .fillna("")
                .astype(str)
            )


    # ---------------------------------------------------
    # PROFILE TO SEARCH TEXT
    # ---------------------------------------------------

    def _profile_text(
        self,
        profile
    ):

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
            "farmer_type",
            "business_type",
        ]

        parts = []

        for field in useful_fields:

            value = profile.get(
                field
            )

            if value not in (
                None,
                "",
                "No"
            ):

                parts.append(
                    str(value)
                )


        age = profile.get(
            "age"
        )

        income = profile.get(
            "annual_income"
        )


        if age is not None:

            parts.append(
                f"age {age}"
            )


        if income is not None:

            parts.append(
                f"annual family income {income}"
            )


        return " ".join(
            parts
        )


    # ---------------------------------------------------
    # HARD ELIGIBILITY FILTER
    # ---------------------------------------------------

    def filter_eligibility(
        self,
        profile
    ):

        filtered_df = (
            self.df.copy()
        )


        if not profile:

            return filtered_df


        # -----------------------------------------------
        # STATE FILTER
        # -----------------------------------------------

        user_state = profile.get(
            "state",
            ""
        )


        if user_state:

            filtered_df = filtered_df[
                filtered_df.apply(
                    lambda row:
                    check_state_eligibility(
                        row,
                        user_state
                    ),
                    axis=1
                )
            ]


        return filtered_df


    # ---------------------------------------------------
    # RECOMMEND
    # ---------------------------------------------------

    def recommend(
        self,
        user_query,
        profile=None,
        top_k=10
    ):

        # FIRST apply eligibility filters
        eligible_df = (
            self.filter_eligibility(
                profile
            )
        )


        if eligible_df.empty:

            return pd.DataFrame()


        # -----------------------------------------------
        # TF-IDF ONLY ON ELIGIBLE SCHEMES
        # -----------------------------------------------

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=50000,
        )


        eligible_matrix = (
            vectorizer.fit_transform(
                eligible_df[
                    "clean_description"
                ]
            )
        )


        profile_text = (
            self._profile_text(
                profile
            )
        )


        combined_query = " ".join(
            value
            for value in [
                user_query,
                profile_text
            ]
            if value
        )


        if not combined_query.strip():

            return pd.DataFrame()


        query_vector = (
            vectorizer.transform(
                [
                    combined_query
                ]
            )
        )


        scores = cosine_similarity(
            query_vector,
            eligible_matrix
        ).flatten()


        results = (
            eligible_df.copy()
        )


        results[
            "match_score"
        ] = (
            scores * 100
        ).round(2)


        results = (
            results
            .sort_values(
                "match_score",
                ascending=False
            )
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
            column
            for column in columns
            if column
            in results.columns
        ]


        return (
            results
            .head(top_k)[
                columns
            ]
        )