import json
import pandas as pd
import os
import re


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

INPUT_FILE = "data/raw/track4_test_scores.json"
OUTPUT_FILE = "data/processed/clean_test_scores.csv"


# --------------------------------------------------
# LOAD JSON
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data)

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
# CLEAN ASSESSMENT ID
# --------------------------------------------------

df["assessment_id"] = (
    df["assessment_id"]
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


df["school_id"] = df["school_id"].apply(clean_school_id)


# --------------------------------------------------
# CLEAN DATE
# --------------------------------------------------

def parse_date(value):

    if pd.isna(value):
        return pd.NaT

    value = str(value).strip()

    if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        return pd.to_datetime(
            value,
            format="%Y-%m-%d",
            errors="coerce"
        )

    if re.match(r"^\d{4}/\d{2}/\d{2}$", value):
        return pd.to_datetime(
            value,
            format="%Y/%m/%d",
            errors="coerce"
        )

    if re.match(r"^\d{2}/\d{2}/\d{4}$", value):
        return pd.to_datetime(
            value,
            format="%d/%m/%Y",
            errors="coerce"
        )

    if re.match(r"^\d{2}\.\d{2}\.\d{4}$", value):
        return pd.to_datetime(
            value,
            format="%d.%m.%Y",
            errors="coerce"
        )

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

    return pd.to_datetime(
        value,
        errors="coerce",
        dayfirst=True
    )


df["date"] = df["date"].apply(parse_date)


# --------------------------------------------------
# CLEAN GRADE
# --------------------------------------------------

roman_grade_map = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5
}


def clean_grade(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().upper()

    if value in roman_grade_map:
        return roman_grade_map[value]

    try:
        return int(float(value))
    except:
        return pd.NA


df["grade"] = df["grade"].apply(clean_grade)


# --------------------------------------------------
# CLEAN SUBJECT
# --------------------------------------------------

def clean_subject(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().lower()

    subject_map = {
        "math": "Math",
        "mathematics": "Math",
        "ganit": "Math",
        "english": "English",
        "hindi": "Hindi",
        "punjabi": "Punjabi",
        "science": "Science",
        "evs": "EVS",
        "environmental studies": "EVS"
    }

    return subject_map.get(
        value,
        value.title()
    )


df["subject"] = df["subject"].apply(clean_subject)


# --------------------------------------------------
# STANDARDIZE GRADING SCALE
# --------------------------------------------------

def clean_grading_scale(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().lower()

    scale_map = {
        "percentage": "Percentage",
        "pct": "Percentage",
        "%": "Percentage",
        "raw marks": "Raw Marks",
        "letter grade": "Letter Grade",
        "cgpa": "CGPA"
    }

    return scale_map.get(
        value,
        value.title()
    )


df["grading_scale"] = df["grading_scale"].apply(
    clean_grading_scale
)


# --------------------------------------------------
# KEEP ORIGINAL SCORE
# --------------------------------------------------

df["original_score"] = (
    df["avg_score"]
    .astype("string")
    .str.strip()
)


# --------------------------------------------------
# CONVERT SCORES TO PERCENTAGE
# --------------------------------------------------

def calculate_percentage(row):

    score = row["original_score"]
    scale = row["grading_scale"]

    if pd.isna(score):
        return pd.NA

    # ----------------------------------------------
    # Percentage / pct / %
    # ----------------------------------------------

    if scale == "Percentage":

        value = str(score).strip()
        value = value.replace("%", "").strip()

        try:
            return float(value)
        except:
            return pd.NA

    # ----------------------------------------------
    # Raw Marks
    # ----------------------------------------------

    if scale == "Raw Marks":

        value = str(score).strip()

        # Example:
        # 21.6/50
        # 16.0/25
        # 83.1/100

        if "/" in value:

            parts = value.split("/")

            if len(parts) == 2:

                try:
                    obtained = float(parts[0])
                    maximum = float(parts[1])

                    if maximum > 0:
                        return round(
                            (obtained / maximum) * 100,
                            2
                        )

                except:
                    return pd.NA

        return pd.NA

    # ----------------------------------------------
    # CGPA
    # ----------------------------------------------

    if scale == "CGPA":

        try:
            value = float(score)

            # Dataset examples use max_marks = 10.
            # Convert to percentage using the
            # supplied 10-point scale.

            return round(
                (value / 10) * 100,
                2
            )

        except:
            return pd.NA

    # ----------------------------------------------
    # Letter Grade
    # ----------------------------------------------

    # No percentage conversion is applied because
    # the dataset does not provide an explicit
    # percentage mapping for A+, A, B, C, D and E.

    if scale == "Letter Grade":
        return pd.NA

    return pd.NA


df["score_percentage"] = df.apply(
    calculate_percentage,
    axis=1
)


# --------------------------------------------------
# CLEAN MAX MARKS
# --------------------------------------------------

def clean_max_marks(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip()

    if value.upper() == "NA":
        return pd.NA

    try:
        return float(value)
    except:
        return pd.NA


df["max_marks"] = df["max_marks"].apply(
    clean_max_marks
)


# --------------------------------------------------
# CLEAN TOTAL STUDENTS ASSESSED
# --------------------------------------------------

df["total_students_assessed"] = pd.to_numeric(
    df["total_students_assessed"],
    errors="coerce"
)


# --------------------------------------------------
# VALIDATION FLAGS
# --------------------------------------------------

df["score_missing"] = (
    df["original_score"].isna() |
    (df["original_score"].str.upper() == "NA")
)

df["percentage_available"] = (
    df["score_percentage"].notna()
)

df["score_outside_valid_range"] = (
    df["score_percentage"].notna() &
    (
        (df["score_percentage"] < 0) |
        (df["score_percentage"] > 100)
    )
)


# --------------------------------------------------
# REMOVE EXACT DUPLICATE ROWS
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
print("TEST SCORES CLEANING REPORT")
print("=" * 50)

print("\nOriginal rows:", before_duplicates)

print(
    "Exact duplicate rows removed:",
    duplicates_removed
)

print(
    "Cleaned rows:",
    len(df)
)


print("\nGrading scales after standardization:")

print(
    df["grading_scale"]
    .value_counts(dropna=False)
)


print("\nSubjects after standardization:")

print(
    df["subject"]
    .value_counts(dropna=False)
)


print("\nMissing values:")

print(
    df.isna().sum()
)


print(
    "\nRecords with percentage available:",
    df["percentage_available"].sum()
)


print(
    "Records without percentage conversion:",
    (~df["percentage_available"]).sum()
)


print(
    "Scores outside 0-100:",
    df["score_outside_valid_range"].sum()
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
            "assessment_id",
            "date",
            "school_id",
            "grade",
            "subject",
            "grading_scale",
            "original_score",
            "score_percentage",
            "max_marks",
            "total_students_assessed"
        ]
    ].head(10)
)


print("\nSaved file:")
print(OUTPUT_FILE)

print("\nTest scores cleaning completed successfully.")