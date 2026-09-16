import pandas as pd
import os
import re


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

INPUT_FILE = "data/raw/track4_school_infrastructure.csv"
OUTPUT_FILE = "data/processed/clean_infrastructure.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("Original rows:", len(df))


# --------------------------------------------------
# CLEAN COLUMN NAMES
# --------------------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)


# --------------------------------------------------
# CLEAN INSPECTION ID
# --------------------------------------------------

df["inspection_id"] = (
    df["inspection_id"]
    .astype("string")
    .str.strip()
    .str.upper()
)


# --------------------------------------------------
# CLEAN SCHOOL ID
# --------------------------------------------------

def clean_school_id(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().upper()

    # Remove spaces, hyphens and underscores
    value = re.sub(r"[\s\-_]", "", value)

    if value.startswith("SCH"):

        number = value[3:]

        if number.isdigit():
            return "SCH" + number.zfill(4)

    elif value.startswith("S"):

        number = value[1:]

        if number.isdigit():
            return "SCH" + number.zfill(4)

    elif value.isdigit():

        return "SCH" + value.zfill(4)

    return value


df["school_id"] = df["school_id"].apply(
    clean_school_id
)


# --------------------------------------------------
# CLEAN DATE
# --------------------------------------------------

def parse_date(value):

    if pd.isna(value):
        return pd.NaT

    value = str(value).strip()

    # YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", value):

        return pd.to_datetime(
            value,
            format="%Y-%m-%d",
            errors="coerce"
        )

    # YYYY/MM/DD
    if re.match(r"^\d{4}/\d{2}/\d{2}$", value):

        return pd.to_datetime(
            value,
            format="%Y/%m/%d",
            errors="coerce"
        )

    # DD/MM/YYYY
    if re.match(r"^\d{2}/\d{2}/\d{4}$", value):

        return pd.to_datetime(
            value,
            format="%d/%m/%Y",
            errors="coerce"
        )

    # DD.MM.YYYY
    if re.match(r"^\d{2}\.\d{2}\.\d{4}$", value):

        return pd.to_datetime(
            value,
            format="%d.%m.%Y",
            errors="coerce"
        )

    # DD-MM-YYYY / MM-DD-YYYY
    if re.match(r"^\d{2}-\d{2}-\d{4}$", value):

        first = int(value[:2])
        second = int(value[3:5])

        if first > 12:

            return pd.to_datetime(
                value,
                format="%d-%m-%Y",
                errors="coerce"
            )

        if second > 12:

            return pd.to_datetime(
                value,
                format="%m-%d-%Y",
                errors="coerce"
            )

        return pd.to_datetime(
            value,
            format="%d-%m-%Y",
            errors="coerce"
        )

    # Handles values such as:
    # 02-Jun-2025

    return pd.to_datetime(
        value,
        errors="coerce",
        dayfirst=True
    )


df["date"] = df["date"].apply(parse_date)


# --------------------------------------------------
# STANDARDIZE BOOLEAN VALUES
# --------------------------------------------------

def clean_boolean(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().lower()

    true_values = {
        "true",
        "yes",
        "y",
        "1",
        "hai",
        "haan",
        "functional",
        "working",
        "available"
    }

    false_values = {
        "false",
        "no",
        "n",
        "0",
        "nahi",
        "nahi hai",
        "kharab",
        "broken",
        "not available"
    }

    if value in true_values:
        return True

    if value in false_values:
        return False

    return pd.NA


boolean_columns = [
    "has_electricity",
    "has_drinking_water",
    "has_functional_toilet",
    "has_boundary_wall",
    "has_playground"
]

for column in boolean_columns:

    df[column] = df[column].apply(
        clean_boolean
    )


# --------------------------------------------------
# CLEAN INSPECTOR NAME
# --------------------------------------------------

df["inspector_name"] = (
    df["inspector_name"]
    .astype("string")
    .str.strip()
)


# --------------------------------------------------
# CLEAN REMARKS
# --------------------------------------------------

df["remarks"] = (
    df["remarks"]
    .astype("string")
    .str.strip()
)


# --------------------------------------------------
# CREATE DATA QUALITY FLAGS
# --------------------------------------------------

for column in boolean_columns:

    flag_name = column + "_missing"

    df[flag_name] = df[column].isna()


# --------------------------------------------------
# FACILITY COUNT
# --------------------------------------------------

df["functional_facility_count"] = (
    df[boolean_columns]
    .eq(True)
    .sum(axis=1)
)


# --------------------------------------------------
# COMPLETE INFRASTRUCTURE FLAG
# --------------------------------------------------

df["all_core_facilities_available"] = (
    df[boolean_columns]
    .notna()
    .all(axis=1)
    &
    df[boolean_columns]
    .eq(True)
    .all(axis=1)
)


# --------------------------------------------------
# EXACT DUPLICATES
# --------------------------------------------------

before_duplicates = len(df)

df = df.drop_duplicates()

duplicates_removed = (
    before_duplicates - len(df)
)


# --------------------------------------------------
# CREATE OUTPUT DIRECTORY
# --------------------------------------------------

os.makedirs(
    "data/processed",
    exist_ok=True
)


# --------------------------------------------------
# SAVE CLEAN DATA
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# VALIDATION REPORT
# --------------------------------------------------

print("\n" + "=" * 50)
print("INFRASTRUCTURE CLEANING REPORT")
print("=" * 50)

print(
    "\nOriginal rows:",
    before_duplicates
)

print(
    "Exact duplicate rows removed:",
    duplicates_removed
)

print(
    "Cleaned rows:",
    len(df)
)


print("\nInfrastructure values after standardization:")

for column in boolean_columns:

    print(
        "\n" + column + ":"
    )

    print(
        df[column]
        .value_counts(dropna=False)
    )


print("\nMissing values:")

print(
    df.isna().sum()
)


print(
    "\nSchools with all core facilities available:",
    df["all_core_facilities_available"].sum()
)


print(
    "Average functional facility count:",
    round(
        df["functional_facility_count"].mean(),
        2
    )
)


if df["date"].notna().any():

    print(
        "\nDate range:",
        df["date"].min(),
        "to",
        df["date"].max()
    )


# --------------------------------------------------
# SAMPLE CLEANED DATA
# --------------------------------------------------

print("\nSample cleaned data:")

print(
    df[
        [
            "inspection_id",
            "date",
            "school_id",
            "has_electricity",
            "has_drinking_water",
            "has_functional_toilet",
            "has_boundary_wall",
            "has_playground",
            "functional_facility_count",
            "all_core_facilities_available"
        ]
    ].head(10)
)


print("\nSaved file:")
print(OUTPUT_FILE)

print(
    "\nInfrastructure cleaning completed successfully."
)