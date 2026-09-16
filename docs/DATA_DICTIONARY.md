# EduPulse — Data Dictionary

> **TransOrg AgentIQ Datathon — Track 4: Education & EdTech**
> Student Retention & Welfare Efficacy Tracker

---

## 1. Purpose

This document describes every dataset used by the EduPulse platform: the raw source files, their cleaned counterparts, the exact transformations applied, validation rules, derived fields, and their meaning in the context of the dashboard and AI query engine.

All column names, formulas, row counts, and cleaning decisions documented here are drawn directly from the repository source code (`src/`) and the processed dataset files. Nothing has been invented or assumed.

---

## 2. Dataset Overview

| # | Dataset | Raw File | Cleaned File | Purpose | Raw Rows | Cleaned Rows |
|---|---------|----------|--------------|---------|----------|--------------|
| 1 | School Master | `data/raw/track4_school_master.csv` | `data/processed/clean_school_master.csv` | Master reference for all schools — join key for every other dataset | 618 | 600 |
| 2 | Student Attendance | `data/raw/track4_student_attendance.csv` | `data/processed/clean_attendance.csv` | Daily grade-level attendance records with anomaly flags | 20,800 | 20,000 |
| 3 | Test Scores | `data/raw/track4_test_scores.json` | `data/processed/clean_test_scores.csv` | FLN assessment records with multi-format score standardization | 8,000 | 8,000 |
| 4 | Mid-Day Meal Procurement | `data/raw/track4_mid_day_meal_procurement.xlsx` | `data/processed/clean_mid_day_meal_procurement.csv` | Grain procurement and payment records for the Mid-Day Meal scheme | 12,360 | 12,000 |
| 5 | School Infrastructure | `data/raw/track4_school_infrastructure.csv` | `data/processed/clean_infrastructure.csv` | Periodic inspection records for five core facility types | 3,150 | 3,000 |
| 6 | School Analytics | *(integrated)* | `data/processed/school_analytics.csv` | One-row-per-school aggregation of all five datasets plus derived risk indicators | — | 600 |

> **Note on Test Scores:** No exact duplicate rows were found in the raw JSON, so the cleaned file retains all 8,000 records. The 1,983 records whose `score_percentage` is missing correspond to Letter Grade entries — see Section 5.

---

## 3. School Master Data Dictionary

**Source script:** `src/clean_school_master.py`

This is the reference table for all 600 unique schools. All other datasets link to it via `school_id`.

| Column | Type | Description | Example | Cleaning Applied | Missing-Value Handling |
|--------|------|-------------|---------|-----------------|----------------------|
| `school_id` | string | Unique school identifier | `SCH0437` | Stripped, uppercased; hyphens and underscores removed | Rows without a parseable ID are excluded by deduplication |
| `school_name` | string | Official name of the school | `Govt. Primary School Nangal` | `.strip()` applied | Retained as-is if present |
| `district` | string | Administrative district name | `Ludhiana` | `.strip()` then `.title()` (title-case) | Filled with `"Unknown"` if missing |
| `block` | string | Administrative block within the district | `Khanna` | `.strip()` then `.title()` | Filled with `"Unknown"` if missing |
| `total_enrolled_students` | float | Total students enrolled at the school | `312` | Converted with `pd.to_numeric(errors="coerce")` | Unparseable values become `NaN` and are retained |
| `school_type` | string | Level of the school | `Primary` | `.strip()` then `.title()` | Retained as-is |
| `medium` | string | Language medium of instruction | `Punjabi` | `.strip()` then `.title()` | Retained as-is |

**Cleaning summary:**
- 18 duplicate `school_id` rows were removed (first occurrence kept).
- Column names were stripped of leading/trailing whitespace.

---

## 4. Student Attendance Data Dictionary

**Source script:** `src/clean_attendance.py`

Each row represents a daily attendance record for one grade at one school.

### 4.1 Source / Raw Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `record_id` | string | Unique identifier for the attendance record | `ATT00001` |
| `date` | string (raw) | Date of attendance (multiple formats in source) | `2025-07-14`, `14/07/2025`, `14-07-2025` |
| `school_id` | string (raw) | School identifier (multiple formats in source) | `SCH0001`, `S001`, `1001`, `SCH-0001` |
| `grade` | string (raw) | Class/grade (numeric or Roman numeral) | `1`, `III`, `5` |
| `total_students` | string (raw) | Count of students enrolled for that grade/day | `45` |
| `present_students` | string (raw) | Count of students physically present | `38` |
| `teacher_present` | string (raw) | Whether the teacher was present (mixed formats) | `Yes`, `Y`, `Haan`, `No`, `N`, `Nahi` |
| `marked_by` | string (raw) | Name/ID of person who marked attendance | `Teacher`, `Principal` |

### 4.2 Cleaned & Derived Columns

| Column | Type | Description | Formula / Rule |
|--------|------|-------------|----------------|
| `record_id` | string | As above; 405 values are `NaN` in source and retained | — |
| `date` | datetime | Parsed from multiple date formats | Custom parser — see Section 10 |
| `school_id` | string | Standardized school ID | `SCH` + zero-padded 4-digit number (e.g., `SCH0001`) |
| `grade` | integer | Numeric grade (1–5); Roman numerals mapped | `I→1, II→2, III→3, IV→4, V→5` |
| `total_students` | float | Numeric count | `pd.to_numeric(errors="coerce")` |
| `present_students` | float | Numeric count | `pd.to_numeric(errors="coerce")` |
| `teacher_present` | boolean | Normalized boolean | `True/Yes/Y/Haan/Hai/Available → True`; `False/No/N/Nahi/Not Available → False`; unknown → `NaN` |
| `marked_by` | string | Trimmed text | `.strip()` |
| `date_outside_expected_range` | boolean | Flag: date is before 2025-04-01 or after 2026-03-31 | `(date < 2025-04-01) OR (date > 2026-03-31)` |
| `date_missing` | boolean | Flag: date could not be parsed | `date.isna()` |
| `attendance_invalid` | boolean | Flag: impossible record — more present than enrolled | `present_students > total_students` |
| `attendance_rate` | float | Calculated attendance percentage | `(present_students / total_students) × 100`, rounded to 2 d.p.; `inf`/`-inf` → `NaN` |
| `is_sunday` | boolean | Flag: the record date falls on a Sunday | `date.dt.dayofweek == 6` |
| `proxy_attendance` | boolean | Flag: 100% attendance marked on a Sunday | `(attendance_rate == 100) AND (is_sunday == True)` |
| `perfect_attendance` | boolean | Flag: attendance rate is exactly 100% | `attendance_rate == 100` |

> **Important:** Flagged records (`attendance_invalid`, `proxy_attendance`) are **retained** in the cleaned dataset. They are not deleted; they are flagged for downstream analysis.

**Missing values after cleaning:**

| Column | Missing Count |
|--------|--------------|
| `record_id` | 405 |
| `teacher_present` | 4,779 |
| `marked_by` | 3,369 |
| All other columns | 0 |

**Anomaly counts:**
- Invalid attendance records (present > total): **806**
- Sunday proxy attendance records: **1,068**
- Perfect attendance (100%) records: **1,651**
- Duplicate rows removed: **800**

---

## 5. Test Scores Data Dictionary

**Source script:** `src/clean_test_scores.py`
**Source format:** JSON array (`track4_test_scores.json`)

Each row represents one FLN (Foundational Literacy and Numeracy) assessment result for a grade at a school.

### 5.1 Source / Raw Columns (from JSON)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `assessment_id` | string | Unique identifier for the assessment record | `ASS00001` |
| `date` | string | Assessment date (multiple formats) | `2025-09-10` |
| `school_id` | string | School identifier (multiple formats) | `SCH0001` |
| `grade` | string | Class/grade | `3`, `IV` |
| `subject` | string | Subject name (mixed English/Hindi) | `Math`, `Ganit`, `English` |
| `grading_scale` | string | Scoring format used | `Percentage`, `pct`, `Raw Marks`, `Letter Grade`, `CGPA` |
| `avg_score` | string | Raw score as recorded | `78.5`, `35/50`, `7.8`, `A+` |
| `max_marks` | string | Maximum possible marks (for Raw Marks scale) | `50`, `100`, `NA` |
| `total_students_assessed` | string | Number of students who sat the assessment | `38` |

### 5.2 Cleaned & Derived Columns

| Column | Type | Description | Cleaning / Formula |
|--------|------|-------------|-------------------|
| `assessment_id` | string | Stripped and uppercased | `.strip().upper()` |
| `date` | datetime | Parsed from multiple formats | Same multi-format parser as Attendance (Section 10) |
| `school_id` | string | Standardized | Same algorithm as Attendance |
| `grade` | integer | Numeric | Roman numeral map + `int(float(value))` |
| `subject` | string | Standardized subject name | `Math/Ganit→Math`, `Environmental Studies/EVS→EVS`, etc. |
| `grading_scale` | string | Standardized scale label | `percentage/pct/%→Percentage`, `raw marks→Raw Marks`, `letter grade→Letter Grade`, `cgpa→CGPA` |
| `max_marks` | float | Maximum marks, numeric | `pd.to_numeric`; `"NA"` → `NaN` |
| `total_students_assessed` | float | Numeric count | `pd.to_numeric(errors="coerce")` |
| `original_score` | string | Exact copy of raw `avg_score` before conversion | `df["avg_score"].astype("string").str.strip()` |
| `score_percentage` | float | Score converted to percentage (0–100) | See conversion rules below |
| `score_missing` | boolean | Flag: original score is null or `"NA"` | `original_score.isna() OR (original_score.upper() == "NA")` |
| `percentage_available` | boolean | Flag: `score_percentage` is not null | `score_percentage.notna()` |
| `score_outside_valid_range` | boolean | Flag: converted score is outside 0–100 | `(score_percentage < 0) OR (score_percentage > 100)` |

### 5.3 Score Standardization Rules

| Grading Scale | Conversion Rule | Result when not convertible |
|--------------|-----------------|----------------------------|
| **Percentage** | Strip `%`, parse as float | `NaN` |
| **Raw Marks** | Parse `obtained/maximum`; compute `(obtained / maximum) × 100` | `NaN` (if format invalid or maximum == 0) |
| **CGPA** | `(value / 10) × 100` (10-point scale as per dataset convention) | `NaN` |
| **Letter Grade** | **No conversion applied.** The source data does not provide an explicit letter-grade-to-percentage mapping. `score_percentage` is set to `NaN`. | `NaN` (always) |

**Counts after cleaning:**

| Scale | Records |
|-------|---------|
| Percentage | 2,406 |
| Raw Marks | 2,002 |
| Letter Grade | 1,983 |
| CGPA | 1,609 |

- Records with `score_percentage` available: **6,017**
- Records where `score_percentage` is `NaN` (Letter Grade): **1,983**
- `score_outside_valid_range` count: **0**
- Duplicate rows removed: **0**

---

## 6. Mid-Day Meal Procurement Data Dictionary

**Source script:** `src/clean_mdm.py`
**Source format:** Excel workbook (`track4_mid_day_meal_procurement.xlsx`)

Each row represents one grain procurement transaction for a school.

### 6.1 Source / Raw Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `procurement_id` | string | Unique transaction identifier | `MDM00001` |
| `date` | string | Transaction date | `2025-08-01` |
| `school_id` | string | School identifier | `SCH0001` |
| `vendor_name` | string | Supplier/vendor name (messy in source) | `Sharma Traders`, `sharma traders pvt ltd` |
| `grain_type` | string | Type of grain (English and Hindi variants) | `Rice`, `Chawal`, `Wheat`, `Gehun` |
| `quantity` | numeric/string | Quantity procured (in original unit) | `50`, `25.5` |
| `unit` | string | Unit of measurement (mixed formats) | `KG`, `g`, `Bag`, `Sack`, `Bori` |
| `total_cost` | string | Cost in INR (messy formats) | `Rs.1250`, `1250/-` |
| `payment_status` | string | Payment status (mixed variants) | `Paid`, `CLEARED`, `Pending`, `Due` |

### 6.2 Cleaned & Derived Columns

| Column | Type | Description | Cleaning / Formula |
|--------|------|-------------|-------------------|
| `procurement_id` | string | Stripped and uppercased | `.strip().upper()` |
| `date` | datetime | Parsed from multiple formats | Same multi-format parser as Attendance (Section 10) |
| `school_id` | string | Standardized | Same algorithm as Attendance |
| `vendor_name` | string | Title-cased and stripped | `.strip().title()` |
| `grain_type` | string | Mapped to standard name | `Gehun→Wheat`, `Chawal→Rice`, `Daal/Pulses/Lentils→Dal`, `Mustard Oil/Cooking Oil/Sarson Tel→Oil` |
| `quantity` | float | Numeric value of quantity in original unit | `pd.to_numeric(errors="coerce")` |
| `unit` | string | Standardized unit code | `kg/kgs/kilogram→KG`, `g/gram/grams→GRAM`, `bag/bags/sack/sacks/bori→BAG_50KG` |
| `total_cost` | float | Cost in INR, numeric | Removes `Rs.`, `Rs`, `/-`, `,`; parses as float |
| `payment_status` | string | Standardized status | `Paid/Cleared→Paid`, `Pending→Pending`, `Due→Due` |
| `quantity_kg` | float | Quantity converted to kilograms | See conversion rules below; rounded to 2 d.p. |
| `quantity_missing` | boolean | Flag: `quantity` is `NaN` | `quantity.isna()` |
| `unit_missing` | boolean | Flag: `unit` is `NaN` | `unit.isna()` |
| `cost_missing` | boolean | Flag: `total_cost` is `NaN` | `total_cost.isna()` |
| `payment_status_missing` | boolean | Flag: `payment_status` is `NaN` | `payment_status.isna()` |
| `quantity_kg_available` | boolean | Flag: `quantity_kg` is not `NaN` | `quantity_kg.notna()` |
| `cost_invalid` | boolean | Flag: `total_cost` is present but negative | `total_cost.notna() AND (total_cost < 0)` |
| `quantity_invalid` | boolean | Flag: `quantity` is present but negative | `quantity.notna() AND (quantity < 0)` |

### 6.3 Quantity Unit Conversion Rules

| Standardized Unit | Conversion to KG |
|------------------|-----------------|
| `KG` | `quantity × 1` (no conversion) |
| `GRAM` | `quantity / 1,000` |
| `BAG_50KG` | `quantity × 50` (1 Bag = 1 Sack = 1 Bori = 50 KG, as per dataset convention in `track4_dataset_notes.txt`) |
| Missing `quantity` or `unit` | `NaN` (no conversion attempted) |

> **Note:** Missing quantities, units, and costs are **not imputed**. They are flagged using the boolean flag columns above and retained as `NaN`.

**Missing values after cleaning:**

| Column | Missing Count |
|--------|--------------|
| `quantity` / `unit` / `quantity_kg` | 3,693 |
| `total_cost` | 625 |
| `payment_status` | 1,668 |
| `cost_invalid` count | 0 |
| `quantity_invalid` count | 0 |

**Payment status distribution:**

| Status | Records |
|--------|---------|
| Paid | 5,157 |
| Pending | 3,388 |
| Due | 1,787 |
| Missing | 1,668 |

- Duplicate rows removed: **360**

---

## 7. Infrastructure Data Dictionary

**Source script:** `src/clean_infrastructure.py`

Each row represents one periodic inspection of a school's physical facilities.

### 7.1 Source / Raw Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `inspection_id` | string | Unique inspection record identifier | `INS00001` |
| `date` | string | Date of inspection | `2025-06-15` |
| `school_id` | string | School identifier | `SCH0001` |
| `has_electricity` | string | Electricity availability (mixed formats) | `Yes`, `1`, `Hai`, `No`, `Kharab` |
| `has_drinking_water` | string | Drinking water availability | `Y`, `Haan`, `0`, `Nahi` |
| `has_functional_toilet` | string | Functional toilet availability | `Working`, `Functional`, `Broken` |
| `has_boundary_wall` | string | Boundary wall availability | `Yes`, `No`, `N` |
| `has_playground` | string | Playground availability | `Available`, `Not Available` |
| `inspector_name` | string | Name of the inspector | `Rajesh Kumar` |
| `remarks` | string | Free-text inspection remarks | `All facilities in order` |

### 7.2 Cleaned & Derived Columns

| Column | Type | Description | Cleaning / Formula |
|--------|------|-------------|-------------------|
| `inspection_id` | string | Stripped and uppercased | `.strip().upper()` |
| `date` | datetime | Parsed from multiple formats | Same multi-format parser as Attendance (Section 10) |
| `school_id` | string | Standardized | Same algorithm as Attendance |
| `has_electricity` | boolean | Normalized boolean | See normalization rules below |
| `has_drinking_water` | boolean | Normalized boolean | See normalization rules below |
| `has_functional_toilet` | boolean | Normalized boolean | See normalization rules below |
| `has_boundary_wall` | boolean | Normalized boolean | See normalization rules below |
| `has_playground` | boolean | Normalized boolean | See normalization rules below |
| `inspector_name` | string | Stripped | `.strip()` |
| `remarks` | string | Stripped | `.strip()` |
| `has_electricity_missing` | boolean | Flag: `has_electricity` is `NaN` after normalization | `has_electricity.isna()` |
| `has_drinking_water_missing` | boolean | Flag: `has_drinking_water` is `NaN` | `has_drinking_water.isna()` |
| `has_functional_toilet_missing` | boolean | Flag: `has_functional_toilet` is `NaN` | `has_functional_toilet.isna()` |
| `has_boundary_wall_missing` | boolean | Flag: `has_boundary_wall` is `NaN` | `has_boundary_wall.isna()` |
| `has_playground_missing` | boolean | Flag: `has_playground` is `NaN` | `has_playground.isna()` |
| `functional_facility_count` | integer | Count of the five facilities that are `True` in this inspection | `sum(has_electricity, has_drinking_water, has_functional_toilet, has_boundary_wall, has_playground)` where each `True` = 1 |
| `all_core_facilities_available` | boolean | Whether all five facilities are non-null and `True` | All five boolean columns are non-null AND all are `True` |

### 7.3 Boolean Normalization Rules

| Raw Value | Normalized To |
|-----------|--------------|
| `true`, `yes`, `y`, `1`, `hai`, `haan`, `functional`, `working`, `available` | `True` |
| `false`, `no`, `n`, `0`, `nahi`, `nahi hai`, `kharab`, `broken`, `not available` | `False` |
| Any other value | `NaN` (unrecognized — retained as missing) |

- Duplicate rows removed: **150**
- Unique schools with infrastructure records: **598** (2 schools from School Master have no inspection records)

---

## 8. Integrated School Analytics Data Dictionary

**Source script:** `src/build_school_analytics.py`
**Output:** `data/processed/school_analytics.csv`

One row per school (600 rows). Built by left-joining all five cleaned datasets onto the School Master using `school_id`.

---

### 8.1 School Information

| Column | Type | Meaning | Source |
|--------|------|---------|--------|
| `school_id` | string | Unique school identifier (join key) | School Master |
| `school_name` | string | Official school name | School Master |
| `district` | string | Administrative district (title-cased) | School Master |
| `block` | string | Administrative block (title-cased) | School Master |
| `total_enrolled_students` | float | Total students enrolled | School Master |
| `school_type` | string | School level (e.g., Primary, Middle) | School Master |
| `medium` | string | Language medium of instruction | School Master |

---

### 8.2 Attendance Metrics

Aggregated from `clean_attendance.csv`, grouped by `school_id`.

| Column | Type | Meaning | Calculation |
|--------|------|---------|-------------|
| `attendance_records` | integer | Total number of attendance records for the school | `COUNT(school_id)` |
| `average_attendance_rate` | float | Mean daily attendance rate across all records | `MEAN(attendance_rate)` |
| `perfect_attendance_records` | integer | Count of records where `perfect_attendance == True` | `SUM(perfect_attendance)` |
| `proxy_attendance_records` | integer | Count of records where `proxy_attendance == True` | `SUM(proxy_attendance)` |
| `invalid_attendance_records` | integer | Count of records where `attendance_invalid == True` | `SUM(attendance_invalid)` |
| `perfect_attendance_rate` | float | % of records with 100% attendance | `(perfect_attendance_records / attendance_records) × 100` |
| `proxy_attendance_rate` | float | % of records flagged as Sunday proxy | `(proxy_attendance_records / attendance_records) × 100` |
| `invalid_attendance_rate` | float | % of records with impossible counts | `(invalid_attendance_records / attendance_records) × 100` |

---

### 8.3 Academic Metrics

Aggregated from `clean_test_scores.csv`, grouped by `school_id`. Only records where `score_percentage` is not `NaN` contribute to `average_test_score`.

| Column | Type | Meaning | Calculation |
|--------|------|---------|-------------|
| `test_records` | integer | Total number of test records for the school | `COUNT(school_id)` |
| `score_records_available` | integer | Records where `score_percentage` is not null | `COUNT(score_percentage)` (non-null count) |
| `average_test_score` | float | Mean converted score percentage | `MEAN(score_percentage)` (null values excluded) |
| `score_conversion_rate` | float | % of test records that have a convertible score | `(score_records_available / test_records) × 100` |

---

### 8.4 Mid-Day Meal Metrics

Aggregated from `clean_mid_day_meal_procurement.csv`, grouped by `school_id`.

| Column | Type | Meaning | Calculation |
|--------|------|---------|-------------|
| `mdm_records` | integer | Total number of MDM procurement records | `COUNT(school_id)` |
| `total_grain_quantity_kg` | float | Total grain procured in kilograms | `SUM(quantity_kg)` |
| `total_mdm_cost` | float | Total procurement cost in INR | `SUM(total_cost)` |
| `paid_records` | integer | Records with `payment_status == "Paid"` | `COUNT WHERE payment_status == "Paid"` |
| `pending_records` | integer | Records with `payment_status == "Pending"` | `COUNT WHERE payment_status == "Pending"` |
| `due_records` | integer | Records with `payment_status == "Due"` | `COUNT WHERE payment_status == "Due"` |
| `payment_status_available` | integer | Records where `payment_status` is not null | `COUNT(payment_status)` (non-null count) |
| `paid_percentage` | float | % of non-null payment records that are "Paid" | `(paid_records / payment_status_available) × 100` |

---

### 8.5 Infrastructure Metrics

Aggregated from `clean_infrastructure.csv`, grouped by `school_id`. Each facility column is the **mean of the boolean values** across all inspections for that school, multiplied by 100 to express as a percentage.

| Column | Type | Meaning | Calculation |
|--------|------|---------|-------------|
| `infrastructure_records` | integer | Number of inspection records for the school | `COUNT(school_id)` |
| `electricity_available` | float | % of inspections where electricity was `True` | `MEAN(has_electricity) × 100` |
| `drinking_water_available` | float | % of inspections where drinking water was `True` | `MEAN(has_drinking_water) × 100` |
| `functional_toilet_available` | float | % of inspections where functional toilet was `True` | `MEAN(has_functional_toilet) × 100` |
| `boundary_wall_available` | float | % of inspections where boundary wall was `True` | `MEAN(has_boundary_wall) × 100` |
| `playground_available` | float | % of inspections where playground was `True` | `MEAN(has_playground) × 100` |
| `average_facility_count` | float | Mean number of functioning facilities per inspection | `MEAN(functional_facility_count)` (scale: 0–5) |
| `all_core_facilities_count` | integer | Count of inspections where all 5 facilities were `True` | `SUM(all_core_facilities_available)` |

> **Note:** 2 schools in School Master have no infrastructure inspection records. Their infrastructure columns and `infrastructure_risk` are `NaN`.

---

### 8.6 Risk Metrics

Derived entirely within `src/build_school_analytics.py`. These are **analytical indicators** only — the source data contains no actual student dropout labels.

| Column | Type | Meaning | Calculation |
|--------|------|---------|-------------|
| `attendance_risk` | float | Risk contribution from low attendance | `100 - average_attendance_rate` |
| `proxy_risk` | float | Risk contribution from proxy attendance fraud | `proxy_attendance_rate` |
| `score_risk` | float | Risk contribution from low academic performance | `100 - average_test_score` |
| `infrastructure_risk` | float | Risk contribution from poor infrastructure | `((5 - average_facility_count) / 5) × 100` |
| `retention_risk_indicator` | float | Composite analytical risk indicator | `MEAN(attendance_risk, proxy_risk, score_risk, infrastructure_risk)` — missing components excluded via `skipna=True` |

---

## 9. Derived Metric Formulas

| Metric | Formula |
|--------|---------|
| **Attendance Rate** | `(present_students / total_students) × 100` |
| **Perfect Attendance Rate** | `(perfect_attendance_records / attendance_records) × 100` |
| **Proxy Attendance Rate** | `(proxy_attendance_records / attendance_records) × 100` |
| **Invalid Attendance Rate** | `(invalid_attendance_records / attendance_records) × 100` |
| **Score Conversion Rate** | `(score_records_available / test_records) × 100` |
| **Paid Percentage** | `(paid_records / payment_status_available) × 100` |
| **Average Facility Count** | `MEAN(functional_facility_count)` per school across all inspections (scale 0–5) |
| **Attendance Risk** | `100 - average_attendance_rate` |
| **Proxy Risk** | `proxy_attendance_rate` |
| **Score Risk** | `100 - average_test_score` |
| **Infrastructure Risk** | `((5 - average_facility_count) / 5) × 100` |
| **Retention Risk Indicator** | `MEAN(attendance_risk, proxy_risk, score_risk, infrastructure_risk)` with `skipna=True` |

> **Critical note:** The `retention_risk_indicator` is an **analytical risk indicator** computed from available operational metrics. It is **not** an actual student dropout probability, a measured dropout rate, or a machine-learning prediction. The source data contains no ground-truth dropout labels.

---

## 10. Data Cleaning & Validation Rules

### School ID Standardization (applied to all five datasets)

All raw school ID variants are normalized to the format `SCHxxxx` (uppercase, 4-digit zero-padded number):

| Raw Format | Normalized |
|------------|-----------|
| `SCH0596` | `SCH0596` |
| `SCH-0212`, `SCH_0212` | `SCH0212` |
| `S0212` | `SCH0212` |
| `0286` | `SCH0286` |

### Date Parsing (applied to all transactional datasets)

A custom `parse_date()` function handles the following formats in priority order:

| Format Pattern | Example |
|---------------|---------|
| `YYYY-MM-DD` | `2025-07-14` |
| `YYYY/MM/DD` | `2025/07/14` |
| `DD/MM/YYYY` | `14/07/2025` |
| `DD.MM.YYYY` | `14.07.2025` |
| `DD-MM-YYYY` | `14-07-2025` (first segment > 12) |
| `MM-DD-YYYY` | `07-26-2025` (second segment > 12) |
| Ambiguous `DD-MM-YYYY` | Treated as `DD-MM-YYYY` by convention |
| `DD-Mon-YYYY` | `10-Apr-2025` (fallback with `dayfirst=True`) |

Unparseable dates become `NaT` and are flagged with `date_missing`.

### Text Normalization

- All text columns: `.strip()` to remove leading/trailing whitespace.
- Column names: `.str.strip().str.lower()` across all scripts.
- Categorical fields (district, block, school_type, medium, subject, grading_scale): `.title()` for consistent capitalization.
- `vendor_name`: `.title()` for consistent capitalization.

### Boolean Normalization (Infrastructure & Attendance)

See Section 7.3 for the full lookup table. Values not in the recognized set become `NaN` (retained, not discarded).

### Numeric Conversion

`pd.to_numeric(errors="coerce")` is used for all numeric columns. Non-numeric strings become `NaN` and are retained.

### Unit Normalization (MDM)

See Section 6.3. The conversion `1 Bag = 1 Sack = 1 Bori = 50 KG` is taken from the dataset convention stated in `track4_dataset_notes.txt`.

### Currency Cleaning (MDM)

Symbols removed: `Rs.`, `Rs`, `/-`, `,`. Remaining string parsed as float.

### Duplicate Handling

Exact duplicate rows are removed in all five datasets using `df.drop_duplicates()`. For School Master, deduplication is on `school_id` only (keeping first occurrence).

### Missing-Value Handling

Missing values are **retained** in cleaned files. Where applicable, boolean flag columns (e.g., `quantity_missing`, `cost_missing`) mark the presence of a missing value explicitly. No imputation is performed on any dataset.

---

## 11. Data Lineage

```
RAW DATA
  track4_school_master.csv
  track4_student_attendance.csv
  track4_test_scores.json
  track4_mid_day_meal_procurement.xlsx
  track4_school_infrastructure.csv
         |
         v
DATA PROFILING
  src/inspect_data.py
  (Column inspection, type checking, value counts)
         |
         v
DATA CLEANING (one script per dataset)
  src/clean_school_master.py
  src/clean_attendance.py
  src/clean_test_scores.py
  src/clean_mdm.py
  src/clean_infrastructure.py
  (School ID standardization, date parsing, boolean normalization,
   score conversion, unit standardization, currency cleaning,
   deduplication, validation flag creation)
         |
         v
DATA VALIDATION
  src/validate_cleaned_data.py
  src/validate_school_ids.py
  src/validate_business_metrics.py
  (Cross-dataset ID matching, business rule checks)
         |
         v
DATA INTEGRATION
  src/build_school_analytics.py
  (Left-join all five cleaned datasets on school_id;
   aggregate per-school metrics; compute risk components)
         |
         v
SCHOOL ANALYTICS DATASET
  data/processed/school_analytics.csv
  (600 rows x 39 columns — one row per school)
         |
         v
DASHBOARD / AI QUERY ENGINE
  dashboard/app.py
  (Streamlit dashboard with KPI cards, charts, district comparisons,
   risk tables, and a natural-language AI query engine)
```

---

## 12. Important Data Limitations

| Limitation | Detail |
|------------|--------|
| No dropout label | The source data contains no ground-truth student dropout labels. The `retention_risk_indicator` is therefore an analytical indicator, not a true dropout prediction. |
| Letter Grade scores | Letter Grades (A+, A, B, C, D, E) are not assigned a percentage because the dataset does not provide an explicit mapping. These 1,983 records have `score_percentage = NaN`. |
| Missing source values | Missing quantities, units, costs, payment statuses, and teacher presence values are retained as `NaN` and flagged — they are not imputed. |
| Infrastructure coverage | 2 schools (of 600) have no infrastructure inspection records; their infrastructure metrics and `infrastructure_risk` are `NaN`. |
| Observational data | All associations (e.g., infrastructure vs. test scores, MDM regularity vs. attendance) are observational. They should not be interpreted as causal effects. |
| Synthetic data | All data is synthetically generated for the TransOrg AgentIQ Datathon. It is designed to simulate realistic education-sector patterns, not to represent actual schools. |
| Date range flags | The `date_outside_expected_range` flag marks records outside 2025-04-01 to 2026-03-31 but does not remove them; the academic year boundary is used for flagging only. |

---

## 13. Data Quality Summary

| Metric | Value |
|--------|-------|
| Total schools in Master | 600 (after removing 18 duplicates) |
| Total attendance records (cleaned) | 20,000 (800 duplicates removed) |
| Total test score records (cleaned) | 8,000 (0 duplicates found) |
| Total MDM procurement records (cleaned) | 12,000 (360 duplicates removed) |
| Total infrastructure inspection records (cleaned) | 3,000 (150 duplicates removed) |
| Unique school IDs across all datasets | 600 (Master); 598 appear in Infrastructure |
| Attendance records flagged as invalid | 806 |
| Attendance records flagged as Sunday proxy | 1,068 |
| Test records with score_percentage available | 6,017 of 8,000 (75.2%) |
| Test records with score_percentage missing (Letter Grade) | 1,983 of 8,000 (24.8%) |
| MDM records with quantity missing | 3,693 of 12,000 (30.8%) |
| MDM records with payment_status missing | 1,668 of 12,000 (13.9%) |
| Analytics rows with any infrastructure NaN | 2–7 (depending on facility column) |
| Analytics rows with retention_risk_indicator missing | 0 (skipna=True in mean calculation) |

---

*Generated from repository source code and data files. Last verified: September 2026.*
