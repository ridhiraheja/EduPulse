import pandas as pd
import json
import os

DATA_PATH = "data/raw"

print("\n========== SCHOOL MASTER ==========")

school = pd.read_csv(
    os.path.join(DATA_PATH, "track4_school_master.csv")
)

print(school.shape)
print(school.columns.tolist())
print(school.head())


print("\n========== ATTENDANCE ==========")

attendance = pd.read_csv(
    os.path.join(DATA_PATH, "track4_student_attendance.csv")
)

print(attendance.shape)
print(attendance.columns.tolist())
print(attendance.head())


print("\n========== TEST SCORES ==========")

with open(
    os.path.join(DATA_PATH, "track4_test_scores.json"),
    "r",
    encoding="utf-8"
) as f:
    scores = json.load(f)

scores = pd.DataFrame(scores)

print(scores.shape)
print(scores.columns.tolist())
print(scores.head())


print("\n========== MDM PROCUREMENT ==========")

mdm = pd.read_excel(
    os.path.join(DATA_PATH, "track4_mid_day_meal_procurement.xlsx")
)

print(mdm.shape)
print(mdm.columns.tolist())
print(mdm.head())


print("\n========== INFRASTRUCTURE ==========")

infra = pd.read_csv(
    os.path.join(DATA_PATH, "track4_school_infrastructure.csv")
)

print(infra.shape)
print(infra.columns.tolist())
print(infra.head())