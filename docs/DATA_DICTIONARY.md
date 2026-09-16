# 📖 EduPulse Data Dictionary

This document provides a comprehensive data dictionary for all raw, cleaned, and integrated datasets within the **EduPulse State Education Intelligence Platform**.

---

## 1. Master School Analytics Dataset (`data/processed/school_analytics.csv`)

| Column Name | Data Type | Description | Source Dataset | Transformation / Formula |
|---|---|---|---|---|
| `school_id` | String | Unique 7-character school identifier (e.g. `SCH0001`) | All Datasets | Standardized & validated |
| `school_name` | String | Official name of the government school | School Master | Capitalized & clean text |
| `district` | String | District administrative location | School Master | Normalized district name |
| `block` | String | Educational block within district | School Master | Standardized block name |
| `school_type` | String | School level (Primary, Middle, Secondary, Higher Secondary) | School Master | Standardized category |
| `medium` | String | Medium of instruction (Punjabi, Hindi, English) | School Master | Normalized spelling |
| `total_enrolled_students` | Integer | Total active student headcount enrolled | School Master | Imputed/Validated |
| `average_attendance_rate` | Float | Mean daily student attendance percentage | Attendance | Mean of daily present % |
| `perfect_attendance_rate` | Float | Percentage of daily records with 100% student presence | Attendance | (Perfect records / Total records) × 100 |
| `proxy_attendance_rate` | Float | Percentage of daily records flagged for proxy marking | Attendance | (Proxy records / Total records) × 100 |
| `invalid_attendance_rate` | Float | Percentage of daily records flagged as invalid/out-of-range | Attendance | (Invalid records / Total records) × 100 |
| `average_test_score` | Float | Average standardized academic test percentage | Test Scores | Unified 0-100% scale mean |
| `score_conversion_rate` | Float | Percentage of test assessments with valid score data | Test Scores | Valid score records / Total tests |
| `total_grain_quantity_kg` | Float | Cumulative grain quantity procured for Mid-Day Meal (kg) | MDM Procurement | Standardized units to KG-equivalent quantities |
| `total_mdm_cost` | Float | Cumulative expenditure on MDM procurement (₹) | MDM Procurement | Sum of cost records |
| `paid_percentage` | Float | Percentage of MDM procurement invoices fully paid | MDM Procurement | (Paid records / Total records) × 100 |
| `electricity_available` | Float | Average facility availability rate across inspection records per school | Infrastructure | Mean inspection status (%) |
| `drinking_water_available` | Float | Average facility availability rate across inspection records per school | Infrastructure | Mean inspection status (%) |
| `functional_toilet_available` | Float | Average facility availability rate across inspection records per school | Infrastructure | Mean inspection status (%) |
| `boundary_wall_available` | Float | Average facility availability rate across inspection records per school | Infrastructure | Mean inspection status (%) |
| `playground_available` | Float | Average facility availability rate across inspection records per school | Infrastructure | Mean inspection status (%) |
| `average_facility_count` | Float | Mean functional core facilities present (0.0 to 5.0) | Infrastructure | Mean count of 5 core facilities |
| `attendance_risk` | Float | Component risk score for attendance deficit | Derived | $100 - \text{average\_attendance\_rate}$ |
| `proxy_risk` | Float | Component risk score for proxy marking anomaly | Derived | $\text{proxy\_attendance\_rate}$ |
| `score_risk` | Float | Component risk score for academic score deficit | Derived | $100 - \text{average\_test\_score}$ |
| `infrastructure_risk` | Float | Component risk score for facility deficit | Derived | $((5.0 - \text{average\_facility\_count}) / 5.0) \times 100$ |
| `retention_risk_indicator` | Float | Composite analytical retention risk index (0-100) | Derived | Mean of 4 component risks |

---

## 2. Cleaned Attendance Dataset (`data/processed/clean_attendance.csv`)

| Column Name | Data Type | Description | Transformation / Business Logic |
|---|---|---|---|
| `record_id` | String | Unique attendance record identifier | Auto-generated UUID |
| `date` | Date | Attendance reporting date (`YYYY-MM-DD`) | Parsed & date range validated |
| `school_id` | String | Foreign key linking to school | Validated against master IDs (100% matched) |
| `grade` | String | Grade level (Grade 1 to Grade 12) | Standardized text format |
| `total_students` | Integer | Enrolled student count for grade | Positive integer enforcement |
| `present_students` | Integer | Present student count reported | Capped at total_students |
| `teacher_present` | Boolean | Teacher attendance indicator | Standardized boolean |
| `attendance_rate` | Float | Daily calculated attendance percentage | $(\text{present} / \text{total}) \times 100$ |
| `proxy_attendance` | Boolean | Flagged proxy marking anomaly | Identified when present = total consistently |
| `perfect_attendance` | Boolean | Flagged 100% presence record | $(\text{present} == \text{total})$ |

---

## 3. Cleaned Test Scores Dataset (`data/processed/clean_test_scores.csv`)

| Column Name | Data Type | Description | Transformation / Business Logic |
|---|---|---|---|
| `assessment_id` | String | Assessment record identifier | Auto-generated UUID |
| `school_id` | String | Foreign key linking to school | Validated against master IDs (100% matched) |
| `grade` | String | Grade level assessed | Standardized text format |
| `subject` | String | Subject (Mathematics, Science, English, Punjabi) | Category normalized |
| `original_score` | Float | Raw test score recorded | Extracted from raw log |
| `max_marks` | Float | Maximum possible score scale | Derived from grading scheme |
| `score_percentage` | Float | Normalized percentage score (0-100%) | $(\text{original\_score} / \text{max\_marks}) \times 100$ |

---

## 4. Cleaned MDM Procurement Dataset (`data/processed/clean_mid_day_meal_procurement.csv`)

| Column Name | Data Type | Description | Transformation / Business Logic |
|---|---|---|---|
| `procurement_id` | String | Procurement record ID | Auto-generated UUID |
| `school_id` | String | Foreign key linking to school | Validated against master IDs (100% matched) |
| `vendor_name` | String | Procurement vendor name | Standardized text |
| `grain_type` | String | Grain item (Wheat, Rice, Pulses) | Category normalized |
| `quantity_kg` | Float | Procurement quantity in kilograms | Standardized procurement units into KG-equivalent quantities |
| `total_cost` | Float | Procurement cost in ₹ | Imputed missing values from unit price |
| `payment_status` | String | Payment status (Paid, Pending, Overdue) | Standardized uppercase category |

---

## 5. Cleaned Infrastructure Inspection Dataset (`data/processed/clean_infrastructure.csv`)

| Column Name | Data Type | Description | Transformation / Business Logic |
|---|---|---|---|
| `inspection_id` | String | Inspection event ID | Auto-generated UUID |
| `school_id` | String | Foreign key linking to school | Validated against master IDs (100% matched; 598 unique schools inspected) |
| `has_electricity` | Boolean | Functional electricity presence | Standardized boolean |
| `has_drinking_water` | Boolean | Functional drinking water presence | Standardized boolean |
| `has_functional_toilet` | Boolean | Functional toilet presence | Standardized boolean |
| `has_boundary_wall` | Boolean | Boundary wall presence | Standardized boolean |
| `has_playground` | Boolean | Playground presence | Standardized boolean |
| `functional_facility_count` | Integer | Total core facilities functional (0 to 5) | Sum of 5 boolean flags |

---

## 6. Retention Risk Indicator Methodology

$$\text{Retention Risk Indicator} = \frac{\text{Attendance Risk} + \text{Proxy Risk} + \text{Score Risk} + \text{Infrastructure Risk}}{4}$$

> **Important Analytical Note:** The *Retention Risk Indicator* is a composite analytical prioritization index designed for administrative decision support. It is **not** a measured student dropout probability, as no explicit dropout label was provided in the raw datasets.
