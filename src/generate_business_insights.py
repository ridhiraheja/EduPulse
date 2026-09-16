import pandas as pd
import os

ANALYTICS_FILE = "data/processed/school_analytics.csv"
INFRA_FILE = "data/processed/clean_infrastructure.csv"
TEST_FILE = "data/processed/clean_test_scores.csv"

OUTPUT_FILE = "outputs/business_insights.txt"

os.makedirs("outputs", exist_ok=True)

analytics = pd.read_csv(ANALYTICS_FILE)
infra = pd.read_csv(INFRA_FILE)
tests = pd.read_csv(TEST_FILE)

# ---------------------------------------------------------
# BASIC OVERVIEW
# ---------------------------------------------------------

total_schools = len(analytics)

total_students = analytics["total_enrolled_students"].sum()

avg_attendance = analytics["average_attendance_rate"].mean()

avg_test_score = analytics["average_test_score"].mean()

avg_facilities = analytics["average_facility_count"].mean()

avg_risk = analytics["retention_risk_indicator"].mean()

# ---------------------------------------------------------
# ATTENDANCE ANOMALIES
# ---------------------------------------------------------

total_proxy = analytics["proxy_attendance_records"].sum()

total_invalid = analytics["invalid_attendance_records"].sum()

avg_proxy_rate = analytics["proxy_attendance_rate"].mean()

avg_invalid_rate = analytics["invalid_attendance_rate"].mean()

# ---------------------------------------------------------
# TOP / LOWEST SCHOOLS
# ---------------------------------------------------------

lowest_attendance = (
    analytics[
        [
            "school_id",
            "school_name",
            "district",
            "average_attendance_rate"
        ]
    ]
    .sort_values("average_attendance_rate")
    .head(10)
)

highest_proxy = (
    analytics[
        [
            "school_id",
            "school_name",
            "district",
            "proxy_attendance_rate"
        ]
    ]
    .sort_values(
        "proxy_attendance_rate",
        ascending=False
    )
    .head(10)
)

lowest_test = (
    analytics[
        [
            "school_id",
            "school_name",
            "district",
            "average_test_score"
        ]
    ]
    .sort_values("average_test_score")
    .head(10)
)

highest_risk = (
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
)

# ---------------------------------------------------------
# LATEST INFRASTRUCTURE INSPECTION PER SCHOOL
# ---------------------------------------------------------

infra["date"] = pd.to_datetime(
    infra["date"],
    errors="coerce"
)

latest_infra = (
    infra
    .sort_values(["school_id", "date"])
    .groupby("school_id")
    .tail(1)
    .copy()
)

# ---------------------------------------------------------
# ELECTRICITY VS TEST PERFORMANCE
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

electricity_scores = dict(
    zip(
        electricity_summary["electricity_status"],
        electricity_summary["average_test_score"]
    )
)

with_electricity = electricity_scores.get(
    "With electricity"
)

without_electricity = electricity_scores.get(
    "Without electricity"
)

if (
    with_electricity is not None
    and without_electricity is not None
):
    electricity_difference = (
        with_electricity -
        without_electricity
    )
else:
    electricity_difference = None

# ---------------------------------------------------------
# INFRASTRUCTURE COVERAGE
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

complete_facilities_count = int(
    latest_infra["complete_facilities"].sum()
)

schools_with_infra = latest_infra[
    "school_id"
].nunique()

schools_without_infra = (
    total_schools -
    schools_with_infra
)

facility_stats = {}

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

    label = (
        column
        .replace("has_", "")
        .replace("_", " ")
        .title()
    )

    facility_stats[label] = (
        available,
        known,
        percentage
    )

# ---------------------------------------------------------
# DISTRICT ANALYSIS
# ---------------------------------------------------------

district_summary = (
    analytics
    .groupby("district")
    .agg(
        schools=("school_id", "nunique"),
        average_attendance=(
            "average_attendance_rate",
            "mean"
        ),
        average_test_score=(
            "average_test_score",
            "mean"
        ),
        average_facilities=(
            "average_facility_count",
            "mean"
        ),
        average_risk=(
            "retention_risk_indicator",
            "mean"
        )
    )
    .sort_values("average_risk", ascending=False)
)

# ---------------------------------------------------------
# ATTENDANCE VS TEST CORRELATION
# ---------------------------------------------------------

correlation = analytics[
    [
        "average_attendance_rate",
        "average_test_score"
    ]
].corr().iloc[0, 1]

# ---------------------------------------------------------
# MDM SUMMARY
# ---------------------------------------------------------

total_mdm_records = analytics[
    "mdm_records"
].sum()

total_mdm_cost = analytics[
    "total_mdm_cost"
].sum()

total_grain_quantity = analytics[
    "total_grain_quantity_kg"
].sum()

average_paid_percentage = analytics[
    "paid_percentage"
].mean()

# ---------------------------------------------------------
# WRITE REPORT
# ---------------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "EDUPULSE - BUSINESS INSIGHTS REPORT\n"
    )

    file.write(
        "=" * 70 + "\n\n"
    )

    file.write("1. OVERALL OVERVIEW\n")
    file.write("-" * 70 + "\n")

    file.write(
        f"Schools analyzed: {total_schools}\n"
    )

    file.write(
        f"Total enrolled students: "
        f"{total_students:,.0f}\n"
    )

    file.write(
        f"Average attendance: "
        f"{avg_attendance:.2f}%\n"
    )

    file.write(
        f"Average test score: "
        f"{avg_test_score:.2f}%\n"
    )

    file.write(
        f"Average facility count: "
        f"{avg_facilities:.2f} / 5\n"
    )

    file.write(
        f"Average retention risk indicator: "
        f"{avg_risk:.2f}\n\n"
    )

    file.write(
        "Note: Retention Risk Indicator is an analytical "
        "measure based on attendance, attendance anomalies, "
        "academic performance and infrastructure conditions. "
        "It is not a measured dropout probability.\n\n"
    )

    # Attendance anomalies
    file.write(
        "2. ATTENDANCE ANOMALIES\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        f"Average proxy attendance rate: "
        f"{avg_proxy_rate:.2f}%\n"
    )

    file.write(
        f"Average invalid attendance rate: "
        f"{avg_invalid_rate:.2f}%\n"
    )

    file.write(
        f"Total proxy attendance records: "
        f"{total_proxy:,.0f}\n"
    )

    file.write(
        f"Total invalid attendance records: "
        f"{total_invalid:,.0f}\n\n"
    )

    # Lowest attendance
    file.write(
        "3. SCHOOLS WITH LOWEST ATTENDANCE\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        lowest_attendance.round(2).to_string(
            index=False
        )
    )

    file.write("\n\n")

    # Highest proxy
    file.write(
        "4. SCHOOLS WITH HIGHEST PROXY ATTENDANCE\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        highest_proxy.round(2).to_string(
            index=False
        )
    )

    file.write("\n\n")

    # Lowest test
    file.write(
        "5. SCHOOLS WITH LOWEST TEST SCORES\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        lowest_test.round(2).to_string(
            index=False
        )
    )

    file.write("\n\n")

    # Highest risk
    file.write(
        "6. HIGHEST RETENTION RISK INDICATORS\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        highest_risk.round(2).to_string(
            index=False
        )
    )

    file.write("\n\n")

    # Electricity
    file.write(
        "7. ELECTRICITY VS TEST PERFORMANCE\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        electricity_summary.round(2).to_string(
            index=False
        )
    )

    if electricity_difference is not None:

        file.write(
            f"\n\nDifference: "
            f"{electricity_difference:.2f} "
            f"percentage points\n"
        )

        file.write(
            "\nInterpretation: Schools with functional "
            "electricity had a slightly different average "
            "test score than schools without functional "
            "electricity. This comparison describes an "
            "association in the available data and does "
            "not establish causation.\n"
        )

    file.write("\n\n")

    # Infrastructure
    file.write(
        "8. INFRASTRUCTURE COVERAGE\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        f"Schools with infrastructure records: "
        f"{schools_with_infra}\n"
    )

    file.write(
        f"Schools without infrastructure records: "
        f"{schools_without_infra}\n"
    )

    file.write(
        f"Schools with all 5 facilities available "
        f"in latest inspection: "
        f"{complete_facilities_count}\n\n"
    )

    for label, values in facility_stats.items():

        available, known, percentage = values

        file.write(
            f"{label}: "
            f"{available}/{known} known "
            f"({percentage:.2f}%)\n"
        )

    file.write("\n")

    # District
    file.write(
        "9. DISTRICT ANALYSIS\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        district_summary.round(2).to_string()
    )

    file.write("\n\n")

    # Correlation
    file.write(
        "10. ATTENDANCE VS TEST PERFORMANCE\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        f"Pearson correlation: "
        f"{correlation:.3f}\n"
    )

    file.write(
        "\nInterpretation: The available school-level data "
        "shows essentially no linear relationship between "
        "average attendance and average test score.\n"
    )

    file.write("\n\n")

    # MDM
    file.write(
        "11. MID-DAY MEAL PROCUREMENT\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        f"Procurement records: "
        f"{total_mdm_records:,.0f}\n"
    )

    file.write(
        f"Total recorded grain quantity: "
        f"{total_grain_quantity:,.2f} kg\n"
    )

    file.write(
        f"Total recorded MDM cost: "
        f"Rs. {total_mdm_cost:,.2f}\n"
    )

    file.write(
        f"Average paid percentage: "
        f"{average_paid_percentage:.2f}%\n"
    )

print(
    f"Business insights report saved to: {OUTPUT_FILE}"
)