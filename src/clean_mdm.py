import pandas as pd
import os
import re


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

INPUT_FILE = "data/raw/track4_mid_day_meal_procurement.xlsx"
OUTPUT_FILE = "data/processed/clean_mid_day_meal_procurement.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_excel(INPUT_FILE)

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
# CLEAN PROCUREMENT ID
# --------------------------------------------------

df["procurement_id"] = (
    df["procurement_id"]
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
    # 10-Apr-2025

    return pd.to_datetime(
        value,
        errors="coerce",
        dayfirst=True
    )


df["date"] = df["date"].apply(parse_date)


# --------------------------------------------------
# CLEAN VENDOR NAME
# --------------------------------------------------

df["vendor_name"] = (
    df["vendor_name"]
    .astype("string")
    .str.strip()
    .str.title()
)


# --------------------------------------------------
# STANDARDIZE GRAIN TYPE
# --------------------------------------------------

def clean_grain(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().lower()

    grain_map = {

        "wheat": "Wheat",
        "gehun": "Wheat",

        "rice": "Rice",
        "chawal": "Rice",

        "dal": "Dal",
        "daal": "Dal",
        "pulses": "Dal",
        "lentils": "Dal",

        "oil": "Oil",
        "mustard oil": "Oil",
        "cooking oil": "Oil",
        "sarson tel": "Oil"
    }

    return grain_map.get(
        value,
        value.title()
    )


df["grain_type"] = df["grain_type"].apply(
    clean_grain
)


# --------------------------------------------------
# CLEAN QUANTITY
# --------------------------------------------------

df["quantity"] = pd.to_numeric(
    df["quantity"],
    errors="coerce"
)


# --------------------------------------------------
# STANDARDIZE UNIT
# --------------------------------------------------

def clean_unit(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().lower()

    unit_map = {

        "kg": "KG",
        "kgs": "KG",
        "kgs.": "KG",
        "kilogram": "KG",
        "kilograms": "KG",

        "g": "GRAM",
        "gram": "GRAM",
        "grams": "GRAM",

        "bag": "BAG_50KG",
        "bags": "BAG_50KG",
        "50kg bags": "BAG_50KG",

        "sack": "BAG_50KG",
        "sacks": "BAG_50KG",

        "bori": "BAG_50KG"
    }

    return unit_map.get(
        value,
        value.upper()
    )


df["unit"] = df["unit"].apply(
    clean_unit
)


# --------------------------------------------------
# CONVERT QUANTITY TO KG
# --------------------------------------------------

def calculate_quantity_kg(row):

    quantity = row["quantity"]
    unit = row["unit"]

    if pd.isna(quantity) or pd.isna(unit):
        return pd.NA

    if unit == "KG":
        return quantity

    if unit == "GRAM":
        return quantity / 1000

    # Source convention:
    # 1 Bag / Sack / Bori = 50 KG

    if unit == "BAG_50KG":
        return quantity * 50

    return pd.NA


df["quantity_kg"] = df.apply(
    calculate_quantity_kg,
    axis=1
)


df["quantity_kg"] = pd.to_numeric(
    df["quantity_kg"],
    errors="coerce"
).round(2)


# --------------------------------------------------
# CLEAN TOTAL COST
# --------------------------------------------------

def clean_cost(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip()

    # Remove currency symbols and text
    value = (
        value
        .replace("₹", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .replace("/-", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(value)
    except:
        return pd.NA


df["total_cost"] = df["total_cost"].apply(
    clean_cost
)


# --------------------------------------------------
# STANDARDIZE PAYMENT STATUS
# --------------------------------------------------

def clean_payment_status(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().upper()

    status_map = {

        "PAID": "Paid",
        "CLEARED": "Paid",

        "PENDING": "Pending",

        "DUE": "Due"
    }

    return status_map.get(
        value,
        value.title()
    )


df["payment_status"] = df["payment_status"].apply(
    clean_payment_status
)


# --------------------------------------------------
# DATA QUALITY FLAGS
# --------------------------------------------------

df["quantity_missing"] = (
    df["quantity"].isna()
)

df["unit_missing"] = (
    df["unit"].isna()
)

df["cost_missing"] = (
    df["total_cost"].isna()
)

df["payment_status_missing"] = (
    df["payment_status"].isna()
)

df["quantity_kg_available"] = (
    df["quantity_kg"].notna()
)

df["cost_invalid"] = (
    df["total_cost"].notna() &
    (df["total_cost"] < 0)
)

df["quantity_invalid"] = (
    df["quantity"].notna() &
    (df["quantity"] < 0)
)


# --------------------------------------------------
# REMOVE EXACT DUPLICATES
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
print("MID-DAY MEAL PROCUREMENT CLEANING REPORT")
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


print("\nGrain types:")

print(
    df["grain_type"]
    .value_counts(dropna=False)
)


print("\nUnits after standardization:")

print(
    df["unit"]
    .value_counts(dropna=False)
)


print("\nPayment statuses:")

print(
    df["payment_status"]
    .value_counts(dropna=False)
)


print("\nMissing values:")

print(
    df.isna().sum()
)


print(
    "\nQuantity missing:",
    df["quantity_missing"].sum()
)

print(
    "Unit missing:",
    df["unit_missing"].sum()
)

print(
    "Cost missing:",
    df["cost_missing"].sum()
)

print(
    "Payment status missing:",
    df["payment_status_missing"].sum()
)

print(
    "Quantity invalid:",
    df["quantity_invalid"].sum()
)

print(
    "Cost invalid:",
    df["cost_invalid"].sum()
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
            "procurement_id",
            "date",
            "school_id",
            "vendor_name",
            "grain_type",
            "quantity",
            "unit",
            "quantity_kg",
            "total_cost",
            "payment_status"
        ]
    ].head(10)
)


print("\nSaved file:")
print(OUTPUT_FILE)

print(
    "\nMid-day meal procurement cleaning completed successfully."
)