import pandas as pd

files = {
    "School Master": "data/processed/clean_school_master.csv",
    "Attendance": "data/processed/clean_attendance.csv",
    "Test Scores": "data/processed/clean_test_scores.csv",
    "MDM Procurement": "data/processed/clean_mid_day_meal_procurement.csv",
    "Infrastructure": "data/processed/clean_infrastructure.csv"
}

print("=" * 70)
print("CLEANED DATA VALIDATION REPORT")
print("=" * 70)

for name, file in files.items():

    df = pd.read_csv(file)

    print("\n" + "-" * 70)
    print(name)
    print("-" * 70)

    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Duplicate rows:", df.duplicated().sum())
    print("Missing values:", df.isna().sum().sum())

    print("\nMissing values by column:")

    missing = df.isna().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print("None")
    else:
        print(missing)

print("\n" + "=" * 70)
print("VALIDATION COMPLETED")
print("=" * 70)