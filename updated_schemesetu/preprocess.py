import os
import re

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


nltk.download("wordnet", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("omw-1.4", quiet=True)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


def clean_text(text):
    if not isinstance(text, str):
        return ""

    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.lower().split()

    return " ".join(
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and len(word) > 2
    )


def preprocess_dataset(
    input_file="updated_data.csv",
    output_file="schemes.csv",
):
    if not os.path.exists(input_file):
        print(f"Dataset not found: {input_file}")
        return None

    print(f"Loading dataset: {input_file}")

    df = pd.read_csv(input_file)

    print(f"Raw rows: {len(df)}")

    # Your uploaded dataset uses these exact source columns.
    source_columns = [
        "scheme_name",
        "details",
        "benefits",
        "eligibility",
        "application",
        "documents",
        "level",
        "schemeCategory",
        "tags",
    ]

    for column in source_columns:
        if column not in df.columns:
            df[column] = ""

        df[column] = df[column].fillna("").astype(str)

    df["name"] = df["scheme_name"].str.strip()

    # Use the important textual fields for semantic search.
    df["description"] = (
        df[
            [
                "details",
                "benefits",
                "eligibility",
                "schemeCategory",
                "tags",
            ]
        ]
        .agg(" ".join, axis=1)
        .str.strip()
    )

    print("Running NLP preprocessing...")

    df["clean_description"] = df["description"].apply(clean_text)

    # Keep only meaningful scheme rows.
    df = df[df["name"] != ""]
    df = df[df["clean_description"] != ""]
    df = df.drop_duplicates(subset=["name"], keep="first")

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nPreprocessing complete.")
    print(f"Processed schemes: {len(df)}")
    print(f"Saved as: {output_file}")

    return df


if __name__ == "__main__":
    preprocess_dataset()
