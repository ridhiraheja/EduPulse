import pandas as pd
import os
import re


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

INPUT_FILE = "data/raw/track4_student_attendance.csv"
OUTPUT_FILE = "data/processed/clean_attendance.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("Original rows:", len(df))


# --------------------------------------------------
# CLEAN COLUMN NAMES
# --------------------------------------------------

df.columns = df.columns.str.strip().str.lower()


# --------------------------------------------------
# CLEAN SCHOOL IDs
# --------------------------------------------------

def clean_school_id(value):
    if pd.isna(value):
        return pd.NA

    value = str(value).strip().upper()

    # Remove spaces, hyphens and underscores
    value = re.sub(r"[\s\-_]", "", value)

    # Convert IDs such as:
    # SCH0596 -> SCH0596
    # S0212   -> SCH0212
    # 0286    -> SCH0286

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

    # DD-MM-YYYY or MM-DD-YYYY
    if re.match(r"^\d{2}-\d{2}-\d{4}$", value):

        first = int(value[:2])
        second = int(value[3:5])

        # Example: 26-07-2025
        if first > 12:
            return pd.to_datetime(
                value,
                format="%d-%m-%Y",
                errors="coerce"
            )

        # Example: 07-26-2025
        if second > 12:
            return pd.to_datetime(
                value,
                format="%m-%d-%Y",
                errors="coerce"
            )

        # Ambiguous case:
        # keep the dataset convention as DD-MM-YYYY
        return pd.to_datetime(
            value,
            format="%d-%m-%Y",
            errors="coerce"
        )

    # Handles values such as:
    # 10-Apr-2025
    return pd.to_datetime(
        value,
        errors="coerce",
        dayfirst=True
    )


df["date"] = df["date"].apply(parse_date)


# --------------------------------------------------
# VALIDATE DATES
# --------------------------------------------------

# Working academic-year reference used only
# to flag potentially unusual dates.
academic_start = pd.Timestamp("2025-04-01")
academic_end = pd.Timestamp("2026-03-31")

df["date_outside_expected_range"] = (
    (df["date"] < academic_start) |
    (df["date"] > academic_end)
)

# Missing dates are handled separately
df["date_missing"] = df["date"].isna()


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

    # Handle numeric grades
    try:
        return int(float(value))
    except:
        return pd.NA


df["grade"] = df["grade"].apply(clean_grade)


# --------------------------------------------------
# CLEAN TEACHER PRESENCE
# --------------------------------------------------

def clean_teacher_presence(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().upper()

    positive_values = {
        "TRUE",
        "YES",
        "Y",
        "HAAN",
        "HAI",
        "AVAILABLE"
    }

    negative_values = {
        "FALSE",
        "NO",
        "N",
        "NAHI",
        "NOT AVAILABLE"
    }

    if value in positive_values:
        return True

    if value in negative_values:
        return False

    return pd.NA


df["teacher_present"] = df["teacher_present"].apply(
    clean_teacher_presence
)


# --------------------------------------------------
# CLEAN STUDENT COUNTS
# --------------------------------------------------

df["total_students"] = pd.to_numeric(
    df["total_students"],
    errors="coerce"
)

df["present_students"] = pd.to_numeric(
    df["present_students"],
    errors="coerce"
)


# --------------------------------------------------
# VALIDATE ATTENDANCE
# --------------------------------------------------

df["attendance_invalid"] = (
    df["present_students"] > df["total_students"]
)


# --------------------------------------------------
# CALCULATE ATTENDANCE RATE
# --------------------------------------------------

df["attendance_rate"] = (
    df["present_students"] /
    df["total_students"] *
    100
)

# Avoid invalid infinite values
df["attendance_rate"] = df["attendance_rate"].replace(
    [float("inf"), float("-inf")],
    pd.NA
)

df["attendance_rate"] = df["attendance_rate"].round(2)


# --------------------------------------------------
# SUNDAY FLAG
# --------------------------------------------------

df["is_sunday"] = (
    df["date"].dt.dayofweek == 6
)


# --------------------------------------------------
# PROXY ATTENDANCE FLAG
# --------------------------------------------------

# 100% attendance recorded on Sunday
df["proxy_attendance"] = (
    (df["attendance_rate"] == 100) &
    (df["is_sunday"])
)


# --------------------------------------------------
# PERFECT ATTENDANCE FLAG
# --------------------------------------------------

df["perfect_attendance"] = (
    df["attendance_rate"] == 100
)


# --------------------------------------------------
# CLEAN MARKED BY
# --------------------------------------------------

df["marked_by"] = (
    df["marked_by"]
    .astype("string")
    .str.strip()
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
# SAVE CLEANED DATA
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# VALIDATION REPORT
# --------------------------------------------------

print("\n" + "=" * 50)
print("ATTENDANCE CLEANING REPORT")
print("=" * 50)

print("\nOriginal rows:", before_duplicates)
print("Exact duplicate rows removed:", duplicates_removed)
print("Cleaned rows:", len(df))


print("\nMissing values:")
print(df.isna().sum())


print(
    "\nInvalid attendance records:",
    df["attendance_invalid"].sum()
)

print(
    "Perfect attendance records:",
    df["perfect_attendance"].sum()
)

print(
    "Sunday proxy attendance records:",
    df["proxy_attendance"].sum()
)

print(
    "Dates outside expected range:",
    df["date_outside_expected_range"].sum()
)

print(
    "Missing dates:",
    df["date_missing"].sum()
)


if df["date"].notna().any():
    print(
        "\nDate range:",
        df["date"].min(),
        "to",
        df["date"].max()
    )


# --------------------------------------------------
# SAMPLE OUTPUT
# --------------------------------------------------

print("\nSample cleaned data:")

print(
    df[
        [
            "record_id",
            "date",
            "school_id",
            "grade",
            "total_students",
            "present_students",
            "teacher_present",
            "attendance_rate",
            "proxy_attendance",
            "date_outside_expected_range"
        ]
    ].head()
)


print("\nSaved file:")
print(OUTPUT_FILE)

print("\nAttendance cleaning completed successfully.")