import pandas as pd
import os

# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

MASTER_FILE = "data/processed/clean_school_master.csv"
ATTENDANCE_FILE = "data/processed/clean_attendance.csv"
TEST_FILE = "data/processed/clean_test_scores.csv"
MDM_FILE = "data/processed/clean_mid_day_meal_procurement.csv"
INFRA_FILE = "data/processed/clean_infrastructure.csv"

OUTPUT_FILE = "data/processed/school_analytics.csv"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

master = pd.read_csv(MASTER_FILE)
attendance = pd.read_csv(ATTENDANCE_FILE)
tests = pd.read_csv(TEST_FILE)
mdm = pd.read_csv(MDM_FILE)
infra = pd.read_csv(INFRA_FILE)


print("=" * 70)
print("BUILDING SCHOOL-LEVEL ANALYTICS DATASET")
print("=" * 70)


# ---------------------------------------------------------
# 1. SCHOOL MASTER
# One row per school
# ---------------------------------------------------------

analytics = master.copy()

print("\nSchool Master schools:", len(analytics))


# ---------------------------------------------------------
# 2. ATTENDANCE METRICS
# ---------------------------------------------------------

attendance_summary = (
    attendance
    .groupby("school_id")
    .agg(
        attendance_records=("school_id", "size"),
        average_attendance_rate=("attendance_rate", "mean"),
        perfect_attendance_records=("perfect_attendance", "sum"),
        proxy_attendance_records=("proxy_attendance", "sum"),
        invalid_attendance_records=("attendance_invalid", "sum")
    )
    .reset_index()
)

attendance_summary["perfect_attendance_rate"] = (
    attendance_summary["perfect_attendance_records"]
    / attendance_summary["attendance_records"]
    * 100
)

attendance_summary["proxy_attendance_rate"] = (
    attendance_summary["proxy_attendance_records"]
    / attendance_summary["attendance_records"]
    * 100
)

attendance_summary["invalid_attendance_rate"] = (
    attendance_summary["invalid_attendance_records"]
    / attendance_summary["attendance_records"]
    * 100
)


analytics = analytics.merge(
    attendance_summary,
    on="school_id",
    how="left"
)


# ---------------------------------------------------------
# 3. TEST SCORE METRICS
# Only records with converted percentage scores
# are included in the average.
# ---------------------------------------------------------

test_summary = (
    tests
    .groupby("school_id")
    .agg(
        test_records=("school_id", "size"),
        score_records_available=("score_percentage", "count"),
        average_test_score=("score_percentage", "mean")
    )
    .reset_index()
)

test_summary["score_conversion_rate"] = (
    test_summary["score_records_available"]
    / test_summary["test_records"]
    * 100
)

analytics = analytics.merge(
    test_summary,
    on="school_id",
    how="left"
)


# ---------------------------------------------------------
# 4. MID-DAY MEAL PROCUREMENT
# ---------------------------------------------------------

mdm_summary = (
    mdm
    .groupby("school_id")
    .agg(
        mdm_records=("school_id", "size"),
        total_grain_quantity_kg=("quantity_kg", "sum"),
        total_mdm_cost=("total_cost", "sum"),
        paid_records=("payment_status", lambda x: (x == "Paid").sum()),
        pending_records=("payment_status", lambda x: (x == "Pending").sum()),
        due_records=("payment_status", lambda x: (x == "Due").sum()),
        payment_status_available=("payment_status", "count")
    )
    .reset_index()
)

mdm_summary["paid_percentage"] = (
    mdm_summary["paid_records"]
    / mdm_summary["payment_status_available"]
    * 100
)

analytics = analytics.merge(
    mdm_summary,
    on="school_id",
    how="left"
)


# ---------------------------------------------------------
# 5. INFRASTRUCTURE
# ---------------------------------------------------------

infra_summary = (
    infra
    .groupby("school_id")
    .agg(
        infrastructure_records=("school_id", "size"),
        electricity_available=("has_electricity", "mean"),
        drinking_water_available=("has_drinking_water", "mean"),
        functional_toilet_available=("has_functional_toilet", "mean"),
        boundary_wall_available=("has_boundary_wall", "mean"),
        playground_available=("has_playground", "mean"),
        average_facility_count=("functional_facility_count", "mean"),
        all_core_facilities_count=("all_core_facilities_available", "sum")
    )
    .reset_index()
)

# Convert boolean averages into percentages
facility_columns = [
    "electricity_available",
    "drinking_water_available",
    "functional_toilet_available",
    "boundary_wall_available",
    "playground_available"
]

for column in facility_columns:
    infra_summary[column] = infra_summary[column] * 100

analytics = analytics.merge(
    infra_summary,
    on="school_id",
    how="left"
)


# ---------------------------------------------------------
# 6. RETENTION RISK INDICATOR
# ---------------------------------------------------------
# This is an analytical indicator, NOT actual dropout
# prediction because the source data has no dropout label.
#
# Higher risk is assigned when:
# - attendance is low
# - proxy attendance is high
# - test performance is low
# - infrastructure availability is low
#
# We create the score only when the corresponding metric
# is available.


analytics["attendance_risk"] = (
    100 - analytics["average_attendance_rate"]
)

analytics["proxy_risk"] = (
    analytics["proxy_attendance_rate"]
)

analytics["score_risk"] = (
    100 - analytics["average_test_score"]
)

analytics["infrastructure_risk"] = (
    (5 - analytics["average_facility_count"]) / 5 * 100
)



risk_components = [
    "attendance_risk",
    "proxy_risk",
    "score_risk",
    "infrastructure_risk"
]

analytics["retention_risk_indicator"] = (
    analytics[risk_components].mean(axis=1, skipna=True)
)

# ---------------------------------------------------------
# 7. ROUND NUMERIC VALUES
# ---------------------------------------------------------

numeric_columns = analytics.select_dtypes(
    include=["float64", "float32"]
).columns

analytics[numeric_columns] = analytics[numeric_columns].round(2)


# ---------------------------------------------------------
# 8. SAVE
# ---------------------------------------------------------

os.makedirs("data/processed", exist_ok=True)

analytics.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# REPORT
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("ANALYTICS DATASET CREATED")
print("=" * 70)

print("Rows:", len(analytics))
print("Columns:", len(analytics.columns))

print("\nColumns:")
for column in analytics.columns:
    print("-", column)

print("\nMissing values in key metrics:")

key_columns = [
    "average_attendance_rate",
    "average_test_score",
    "total_grain_quantity_kg",
    "total_mdm_cost",
    "average_facility_count",
    "retention_risk_indicator"
]

print(analytics[key_columns].isna().sum())

print("\nRetention risk summary:")
print(
    analytics["retention_risk_indicator"]
    .describe()
)

print("\nTop 10 schools by retention risk:")

print(
    analytics[
        [
            "school_id",
            "school_name",
            "district",
            "average_attendance_rate",
            "average_test_score",
            "average_facility_count",
            "retention_risk_indicator"
        ]
    ]
    .sort_values(
        "retention_risk_indicator",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)

print("\nSaved file:")
print(OUTPUT_FILE)

print("\nSchool-level analytics completed successfully.")