import pandas as pd

files = {
    "School Master": "data/processed/clean_school_master.csv",
    "Attendance": "data/processed/clean_attendance.csv",
    "Test Scores": "data/processed/clean_test_scores.csv",
    "MDM Procurement": "data/processed/clean_mid_day_meal_procurement.csv",
    "Infrastructure": "data/processed/clean_infrastructure.csv"
}

datasets = {}

print("=" * 60)
print("SCHOOL ID VALIDATION REPORT")
print("=" * 60)

for name, file in files.items():
    df = pd.read_csv(file)
    datasets[name] = df

    unique_ids = df["school_id"].nunique()

    print(f"\n{name}")
    print(f"Rows: {len(df)}")
    print(f"Unique school IDs: {unique_ids}")

master_ids = set(datasets["School Master"]["school_id"].dropna().unique())

print("\n" + "=" * 60)
print("CHECKING IDs AGAINST SCHOOL MASTER")
print("=" * 60)

for name, df in datasets.items():

    if name == "School Master":
        continue

    ids = set(df["school_id"].dropna().unique())

    missing_from_master = ids - master_ids

    print(f"\n{name}")
    print(f"Unique IDs: {len(ids)}")
    print(f"IDs not found in School Master: {len(missing_from_master)}")

    if missing_from_master:
        print("Sample unmatched IDs:")
        print(sorted(missing_from_master)[:10])

print("\n" + "=" * 60)
print("VALIDATION COMPLETED")
print("=" * 60)