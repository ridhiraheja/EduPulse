import pandas as pd

MASTER_FILE = "data/processed/clean_school_master.csv"
INFRA_FILE = "data/processed/clean_infrastructure.csv"
TEST_FILE = "data/processed/clean_test_scores.csv"

master = pd.read_csv(MASTER_FILE)
infra = pd.read_csv(INFRA_FILE)
tests = pd.read_csv(TEST_FILE)

print("=" * 70)
print("BUSINESS METRIC VALIDATION")
print("=" * 70)


# ---------------------------------------------------------
# 1. LATEST INFRASTRUCTURE INSPECTION PER SCHOOL
# ---------------------------------------------------------

infra["date"] = pd.to_datetime(infra["date"], errors="coerce")

latest_infra = (
    infra
    .sort_values(["school_id", "date"])
    .groupby("school_id")
    .tail(1)
    .copy()
)

print("\nLatest infrastructure inspections:", len(latest_infra))


# ---------------------------------------------------------
# 2. ELECTRICITY VS TEST SCORE
# ---------------------------------------------------------

electricity_test = tests.merge(
    latest_infra[
        ["school_id", "has_electricity"]
    ],
    on="school_id",
    how="inner"
)

electricity_test = electricity_test[
    electricity_test["score_percentage"].notna()
]

electricity_test["electricity_status"] = (
    electricity_test["has_electricity"]
    .map({
        True: "With electricity",
        False: "Without electricity"
    })
)

electricity_test = electricity_test[
    electricity_test["electricity_status"].notna()
]

electricity_summary = (
    electricity_test
    .groupby("electricity_status")
    .agg(
        schools=("school_id", "nunique"),
        test_records=("score_percentage", "count"),
        average_test_score=("score_percentage", "mean")
    )
    .reset_index()
)

print("\n" + "=" * 70)
print("ELECTRICITY VS TEST PERFORMANCE")
print("=" * 70)

print(
    electricity_summary.round(2).to_string(index=False)
)

if len(electricity_summary) == 2:

    scores = dict(
        zip(
            electricity_summary["electricity_status"],
            electricity_summary["average_test_score"]
        )
    )

    with_electricity = scores.get("With electricity")
    without_electricity = scores.get("Without electricity")

    difference = with_electricity - without_electricity

    print(
        f"\nDifference: {difference:.2f} percentage points"
    )


# ---------------------------------------------------------
# 3. COMPLETE INFRASTRUCTURE COVERAGE
# ---------------------------------------------------------

facility_columns = [
    "has_electricity",
    "has_drinking_water",
    "has_functional_toilet",
    "has_boundary_wall",
    "has_playground"
]

latest_infra["complete_facilities"] = (
    latest_infra[facility_columns]
    .notna()
    .all(axis=1)
    &
    latest_infra[facility_columns]
    .eq(True)
    .all(axis=1)
)

complete_count = latest_infra[
    "complete_facilities"
].sum()

print("\n" + "=" * 70)
print("INFRASTRUCTURE COVERAGE")
print("=" * 70)

print(
    "Schools with all 5 facilities in latest inspection:",
    int(complete_count)
)

print(
    "Schools with infrastructure records:",
    latest_infra["school_id"].nunique()
)


# ---------------------------------------------------------
# 4. FACILITY AVAILABILITY
# ---------------------------------------------------------

print("\nFacility availability in latest inspection:")

for column in facility_columns:

    available = (
        latest_infra[column] == True
    ).sum()

    known = (
        latest_infra[column].notna()
    ).sum()

    percentage = (
        available / known * 100
        if known > 0
        else 0
    )

    label = column.replace(
        "has_", ""
    ).replace("_", " ").title()

    print(
        f"{label}: "
        f"{available}/{known} known inspections "
        f"({percentage:.2f}%)"
    )


# ---------------------------------------------------------
# 5. INFRASTRUCTURE COVERAGE
# ---------------------------------------------------------

print("\nInfrastructure records by school:")

print(
    latest_infra["school_id"]
    .nunique()
)

missing_infra_schools = (
    set(master["school_id"])
    -
    set(latest_infra["school_id"])
)

print(
    "Schools without infrastructure record:",
    len(missing_infra_schools)
)


print("\n" + "=" * 70)
print("VALIDATION COMPLETED")
print("=" * 70)