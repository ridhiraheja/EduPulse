# EduPulse | State Education Intelligence & Retention Platform

EduPulse is an enterprise-grade education analytics, decision-support, and agentic AI platform built to analyze student attendance, academic performance, infrastructure readiness, and mid-day meal operations across government schools.

---

## 📌 Executive Summary

Government education departments collect vast volumes of administrative data across disparate domains. However, missing values, inconsistent encodings, proxy marking anomalies, and unlinked datasets obscure actionable policy insights.

**EduPulse** solves this challenge through a multi-stage architecture:
1. **Data Rescue Engine**: Standardizes, cleans, deduplicates, and fuses 5 raw datasets into a unified 600-school master analytics database with 100% School-ID match integrity.
2. **Executive Intelligence Dashboard**: A responsive Streamlit dashboard featuring multi-pillar district benchmarks, interactive 360° school diagnostics, and priority intervention queues.
3. **Agentic AI Query Engine ("Ask EduPulse AI")**: A modular agentic natural-language query engine with dynamic intent resolution (`COMPARISON`, `TREND`, `RANKING`, `CORRELATION`, `ANOMALY`), dynamic Plotly visualization selection, and evidence-based data-derived insights.
4. **Policy Impact Simulator**: An interactive policy planning simulator that recalculates projected retention risk using exact mathematical component scoring.

---

##  Data Rescue & Pipeline Summary

The EduPulse Data Rescue engine successfully ingested, cleaned, and integrated 5 raw datasets:

| Dataset Domain | Raw Input Rows | Cleaned Output Rows | Anomalies & Dupes Cleaned | Key Engineering Transformations |
|---|---|---|---|---|
| **School Master** | 618 | 600 | 18 | Fixed duplicate IDs, standardized text encoding & medium names |
| **Attendance Records** | 20,800 | 20,000 | 800 | Detected 5.1% proxy attendance, flagged invalid dates & non-school days |
| **Test Scores** | 8,000 | 8,000 | 0 | Converted heterogeneous grading scales to unified 0-100% scores |
| **MDM Procurement** | 12,360 | 12,000 | 360 | Standardized procurement units into KG-equivalent quantities, normalized costs |
| **Infrastructure Inspection** | 3,150 | 3,000 | 150 | Standardized boolean flags, aggregated facility availability score per school |

### Core Data Validation & Quality Checks
- ✅ **School Master IDs**: 600 / 600 unique schools.
- ✅ **Attendance Records**: 100% IDs matched (20,000 / 20,000).
- ✅ **Test Scores**: 100% IDs matched (8,000 / 8,000).
- ✅ **MDM Procurement**: 100% IDs matched (12,000 / 12,000).
- ✅ **Infrastructure**: 100% IDs matched (3,000 / 3,000; 598 unique schools inspected).
- ✅ **Unmapped School IDs**: 0 unmapped across all datasets.

---

##  Retention Risk Indicator Methodology

The **Retention Risk Indicator** is a composite analytical prioritization metric (0–100) computed as the arithmetic mean of four 0–100 component risk scores:

$$\text{Retention Risk Indicator} = \frac{\text{Attendance Risk} + \text{Proxy Risk} + \text{Score Risk} + \text{Infrastructure Risk}}{4}$$

Where:
- $\text{Attendance Risk} = 100 - \text{Average Attendance Rate}$
- $\text{Proxy Risk} = \text{Proxy Attendance Rate}$
- $\text{Score Risk} = 100 - \text{Average Test Score}$
- $\text{Infrastructure Risk} = \frac{5.0 - \text{Average Facility Count}}{5.0} \times 100$

> **Methodological Note:** The *Retention Risk Indicator* is an analytical index for administrative decision support. It is **not** a measured dropout probability, as no explicit dropout label was present in the raw source datasets.

---

##  Ask EduPulse AI — Modular Agentic Natural Language Engine

The **Ask EduPulse AI** engine converts freeform natural language questions into data analyses using a modular reasoning pipeline:

```text
Query Input → Intent Detection → Dataset & Column Selection → Dynamic Visualization Selection → Data-Derived Insight
```

### Supported Intent Types & Dynamic Visualizations:
1. **COMPARISON**: Compares metrics between groups (e.g. Electricity vs Test Scores) $\rightarrow$ Renders Grouped Bar Chart with exact measured difference.
2. **TIME-SERIES TREND**: Aggregates date-level reporting (e.g. Attendance over time) $\rightarrow$ Renders Time-Series Line Chart with min/max/mean metrics.
3. **RANKING**: Sorts geographic/administrative entities (e.g. District Risk Index) $\rightarrow$ Renders Horizontal Bar Chart highlighting primary risk drivers.
4. **CORRELATION**: Evaluates bivariate relationships (e.g. Attendance vs Test Performance) $\rightarrow$ Renders Scatter Plot with Pearson $r$ coefficient ($r = -0.002$).
5. **ANOMALY DETECTION**: Filters records above anomaly thresholds (e.g. Proxy Rate > 5%) $\rightarrow$ Renders Ranked Alert Table.

---

##  Policy Impact Simulator

The Policy Impact Simulator empowers education planners to simulate target interventions:
- **Sliders**: Attendance Boost (+%), Remedial Academic Support (+%), Infrastructure Upgrade (+Facilities), Proxy Anomaly Reduction (-%).
- **Calculation**: Recalculates all four component risk scores and projects net reduction in the Retention Risk Indicator.
- **Policy Summary**: Displays baseline risk, projected risk, index point reduction, and relative risk-index reduction percentage.

---

##  Installation & Local Execution

### Prerequisites
- Python 3.10+
- Virtual Environment (`venv`)

### Setup Instructions

1. **Clone the Repository & Navigate to Workspace**:
   ```bash
   cd EduPulse
   ```

2. **Activate Virtual Environment & Install Dependencies**:
   ```bash
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Run Data Cleaning & Pipeline Scripts (Optional / Verification)**:
   ```bash
   python src/clean_school_master.py
   python src/clean_attendance.py
   python src/clean_test_scores.py
   python src/clean_mdm.py
   python src/clean_infrastructure.py
   python src/build_school_analytics.py
   ```

4. **Launch the Executive Streamlit Dashboard**:
   ```bash
   streamlit run dashboard/app.py
   ```

5. Open your browser and navigate to **`http://localhost:8501`**.

---

##  Repository Structure

```text
EduPulse/
├── dashboard/
│   └── app.py                      # Executive Streamlit Dashboard & Agentic AI Engine
├── data/
│   ├── raw/                        # Original raw datasets
│   └── processed/                  # Cleaned, standardized, & integrated CSVs
│       ├── clean_school_master.csv
│       ├── clean_attendance.csv
│       ├── clean_test_scores.csv
│       ├── clean_mid_day_meal_procurement.csv
│       ├── clean_infrastructure.csv
│       └── school_analytics.csv
├── docs/
│   └── DATA_DICTIONARY.md          # Comprehensive Data Dictionary
├── outputs/
│   └── business_insights.txt       # Executive insights summary report
├── src/                            # Data Rescue & ETL Scripts
│   ├── clean_school_master.py
│   ├── clean_attendance.py
│   ├── clean_test_scores.py
│   ├── clean_mdm.py
│   ├── clean_infrastructure.py
│   ├── build_school_analytics.py
│   └── generate_business_insights.py
├── requirements.txt                # Python package dependencies
└── README.md                       # Project documentation
```

---

## 📌 Analytical Boundaries & Methodological Limitations

- **No Measured Dropout Label**: Source datasets do not include explicit dropout event labels; the *Retention Risk Indicator* is an analytical prioritization index.
- **Observational Data**: Statistical comparisons (e.g. electricity availability vs test scores) show association, not direct causation.
- **Infrastructure Inspections**: Infrastructure facility status represents the average facility availability rate across inspection records per school.

- Deployed App link : https://edupulse-ai-tracker.streamlit.app/
- Demo Video link : https://drive.google.com/file/d/10q2-vncuTojwN_XVIP4b4fveG5gfdNHs/view?usp=drive_link
