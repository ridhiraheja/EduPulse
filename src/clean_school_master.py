import pandas as pd
import os

# ---------------------------------------------------
# 1. File paths
# ---------------------------------------------------

INPUT_FILE = "data/raw/track4_school_master.csv"
OUTPUT_FILE = "data/processed/clean_school_master.csv"


# ---------------------------------------------------
# 2. Read the raw data
# ---------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("Original rows:", len(df))


# ---------------------------------------------------
# 3. Remove unnecessary spaces from column names
# ---------------------------------------------------

df.columns = df.columns.str.strip()


# ---------------------------------------------------
# 4. Clean school_id
# ---------------------------------------------------

df["school_id"] = (
    df["school_id"]
    .astype(str)
    .str.strip()
    .str.upper()
    .str.replace("-", "", regex=False)
    .str.replace("_", "", regex=False)
)


# ---------------------------------------------------
# 5. Clean text columns
# ---------------------------------------------------

text_columns = [
    "school_name",
    "district",
    "block",
    "school_type",
    "medium"
]

for column in text_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# ---------------------------------------------------
# 6. Standardize capitalization
# ---------------------------------------------------

df["district"] = df["district"].str.title()
df["block"] = df["block"].str.title()
df["school_type"] = df["school_type"].str.title()
df["medium"] = df["medium"].str.title()


# ---------------------------------------------------
# 7. Handle missing district/block
# ---------------------------------------------------

df["district"] = df["district"].fillna("Unknown")
df["block"] = df["block"].fillna("Unknown")


# ---------------------------------------------------
# 8. Remove duplicate school IDs
# ---------------------------------------------------

before_duplicates = len(df)

df = df.drop_duplicates(
    subset=["school_id"],
    keep="first"
)

duplicates_removed = before_duplicates - len(df)


# ---------------------------------------------------
# 9. Make sure enrolled students is numeric
# ---------------------------------------------------

df["total_enrolled_students"] = pd.to_numeric(
    df["total_enrolled_students"],
    errors="coerce"
)


# ---------------------------------------------------
# 10. Save cleaned dataset
# ---------------------------------------------------

os.makedirs("data/processed", exist_ok=True)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------
# 11. Print cleaning report
# ---------------------------------------------------

print("\n========== SCHOOL MASTER CLEANING REPORT ==========")

print("Original rows:", before_duplicates)
print("Duplicate rows removed:", duplicates_removed)
print("Cleaned rows:", len(df))

print("\nMissing values after cleaning:")
print(df.isnull().sum())

print("\nSample cleaned data:")
print(df.head())

print("\nCleaned file saved to:")
print(OUTPUT_FILE)