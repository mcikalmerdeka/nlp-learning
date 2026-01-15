# WRS Health EHR Database Documentation

## Database Overview

The WRS Health EHR (Electronic Health Record) database is designed to support comprehensive healthcare operations including patient management, clinical workflows, billing, and quality reporting. This PostgreSQL database contains 8 interconnected tables that store information about facilities, insurance plans, patients, providers, appointments, diagnoses, prescriptions, and laboratory results.

**Database Name:** `wrs_health_ehr`  
**Total Tables:** 8  
**Records per Table:** 1,000 sample records

---

## Table Descriptions

### 1. facilities

Stores information about healthcare facilities where medical services are provided.

**Table Name:** `facilities`  
**Primary Key:** `facility_id`

#### Columns:

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|-------------|
| facility_id | VARCHAR(20) | NO | Primary key. Unique identifier for each facility (Format: FAC######) |
| facility_name | VARCHAR(200) | NO | Name of the healthcare facility |
| facility_type | VARCHAR(50) | NO | Type of facility (Hospital, Clinic, Urgent Care, Specialty Center, Outpatient Center, Ambulatory Center) |
| address | VARCHAR(300) | YES | Street address of the facility |
| city | VARCHAR(100) | YES | City where the facility is located |
| state | VARCHAR(2) | YES | Two-letter state code |
| zip_code | VARCHAR(10) | YES | Postal code (5-digit format) |
| phone | VARCHAR(20) | YES | Contact phone number (Format: 555-XXX-XXXX) |
| total_beds | INTEGER | YES | Total number of beds available (NULL for facilities without bed capacity) |
| is_active | BOOLEAN | YES | Indicates if the facility is currently active (TRUE/FALSE) |
| created_date | TIMESTAMP | YES | Date and time when the facility record was created |

#### Relationships:
- Referenced by `providers.facility_id` (One-to-Many: One facility can have multiple providers)
- Referenced by `appointments.facility_id` (One-to-Many: One facility can host multiple appointments)

---

### 2. insurance_plans

Contains information about insurance plans accepted by the healthcare system.

**Table Name:** `insurance_plans`  
**Primary Key:** `plan_id`

#### Columns:

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|-------------|
| plan_id | VARCHAR(20) | NO | Primary key. Unique identifier for each insurance plan (Format: INS######) |
| insurance_company | VARCHAR(200) | NO | Name of the insurance company (e.g., Blue Cross Blue Shield, Aetna, UnitedHealthcare) |
| plan_name | VARCHAR(200) | NO | Specific name of the insurance plan |
| plan_type | VARCHAR(50) | NO | Type of insurance plan (HMO, PPO, EPO, POS) |
| copay_amount | DECIMAL(10,2) | YES | Standard copayment amount in USD for office visits |
| deductible_amount | DECIMAL(10,2) | YES | Annual deductible amount in USD |
| out_of_pocket_max | DECIMAL(10,2) | YES | Maximum out-of-pocket expense limit in USD |
| is_active | BOOLEAN | YES | Indicates if the plan is currently active and accepting enrollments |
| created_date | TIMESTAMP | YES | Date and time when the plan record was created |

#### Relationships:
- Referenced by `patients.primary_insurance_id` (One-to-Many: One plan can cover multiple patients)
- Referenced by `patients.secondary_insurance_id` (One-to-Many: One plan can be secondary coverage for multiple patients)

---

### 3. patients

Stores comprehensive demographic and contact information for patients.

**Table Name:** `patients`  
**Primary Key:** `patient_id`  
**Foreign Keys:** `primary_insurance_id`, `secondary_insurance_id`

#### Columns:

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|-------------|
| patient_id | VARCHAR(20) | NO | Primary key. Unique identifier for each patient (Format: PAT######) |
| mrn | VARCHAR(20) | NO | Medical Record Number - unique identifier used across the healthcare system |
| first_name | VARCHAR(100) | NO | Patient's first name |
| last_name | VARCHAR(100) | NO | Patient's last name |
| date_of_birth | DATE | NO | Patient's date of birth (Format: YYYY-MM-DD) |
| gender | VARCHAR(20) | YES | Patient's gender (Male, Female, Other) |
| ssn | VARCHAR(11) | YES | Social Security Number (Format: XXX-XX-XXXX) - encrypted in production |
| phone | VARCHAR(20) | YES | Primary contact phone number (Format: 555-XXX-XXXX) |
| email | VARCHAR(150) | YES | Email address for patient communications |
| address | VARCHAR(300) | YES | Street address |
| city | VARCHAR(100) | YES | City of residence |
| state | VARCHAR(2) | YES | Two-letter state code |
| zip_code | VARCHAR(10) | YES | Postal code (5-digit format) |
| emergency_contact_name | VARCHAR(200) | YES | Full name of emergency contact person |
| emergency_contact_phone | VARCHAR(20) | YES | Phone number for emergency contact |
| primary_insurance_id | VARCHAR(20) | YES | Foreign key referencing insurance_plans.plan_id for primary coverage |
| secondary_insurance_id | VARCHAR(20) | YES | Foreign key referencing insurance_plans.plan_id for secondary coverage (if applicable) |
| blood_type | VARCHAR(5) | YES | Patient's blood type (A+, A-, B+, B-, AB+, AB-, O+, O-) |
| is_active | BOOLEAN | YES | Indicates if the patient is currently active in the system |
| registration_date | TIMESTAMP | YES | Date and time when the patient was registered |

#### Relationships:
- References `insurance_plans.plan_id` via `primary_insurance_id` (Many-to-One)
- References `insurance_plans.plan_id` via `secondary_insurance_id` (Many-to-One)
- Referenced by `appointments.patient_id` (One-to-Many: One patient can have multiple appointments)
- Referenced by `diagnoses.patient_id` (One-to-Many: One patient can have multiple diagnoses)
- Referenced by `prescriptions.patient_id` (One-to-Many: One patient can have multiple prescriptions)
- Referenced by `lab_results.patient_id` (One-to-Many: One patient can have multiple lab results)

---

### 4. providers

Contains information about healthcare providers (physicians, nurse practitioners, physician assistants).

**Table Name:** `providers`  
**Primary Key:** `provider_id`  
**Foreign Keys:** `facility_id`

#### Columns:

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|-------------|
| provider_id | VARCHAR(20) | NO | Primary key. Unique identifier for each provider (Format: PRV######) |
| npi | VARCHAR(10) | NO | National Provider Identifier - unique 10-digit identification number |
| first_name | VARCHAR(100) | NO | Provider's first name |
| last_name | VARCHAR(100) | NO | Provider's last name |
| specialty | VARCHAR(100) | NO | Primary medical specialty (e.g., Family Medicine, Cardiology, Pediatrics) |
| sub_specialty | VARCHAR(100) | YES | Sub-specialty if applicable (e.g., Interventional, Sports Medicine, Geriatrics) |
| degree | VARCHAR(20) | YES | Medical degree (MD, DO, NP, PA) |
| license_number | VARCHAR(50) | YES | State medical license number |
| license_state | VARCHAR(2) | YES | State where the provider is licensed |
| facility_id | VARCHAR(20) | YES | Foreign key referencing facilities.facility_id - primary practice location |
| phone | VARCHAR(20) | YES | Direct contact phone number |
| email | VARCHAR(150) | YES | Professional email address |
| is_accepting_patients | BOOLEAN | YES | Indicates if the provider is currently accepting new patients |
| is_active | BOOLEAN | YES | Indicates if the provider is currently active in the system |
| hire_date | DATE | YES | Date when the provider was hired |
| created_date | TIMESTAMP | YES | Date and time when the provider record was created |

#### Relationships:
- References `facilities.facility_id` (Many-to-One: Multiple providers can work at one facility)
- Referenced by `appointments.provider_id` (One-to-Many: One provider can have multiple appointments)
- Referenced by `diagnoses.provider_id` (One-to-Many: One provider can make multiple diagnoses)
- Referenced by `prescriptions.provider_id` (One-to-Many: One provider can write multiple prescriptions)
- Referenced by `lab_results.provider_id` (One-to-Many: One provider can order multiple lab tests)

---

### 5. appointments

Tracks all patient appointments including scheduling, status, and visit details.

**Table Name:** `appointments`  
**Primary Key:** `appointment_id`  
**Foreign Keys:** `patient_id`, `provider_id`, `facility_id`

#### Columns:

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|-------------|
| appointment_id | VARCHAR(20) | NO | Primary key. Unique identifier for each appointment (Format: APT######) |
| patient_id | VARCHAR(20) | NO | Foreign key referencing patients.patient_id |
| provider_id | VARCHAR(20) | NO | Foreign key referencing providers.provider_id |
| facility_id | VARCHAR(20) | NO | Foreign key referencing facilities.facility_id where appointment takes place |
| appointment_date | DATE | NO | Date of the scheduled appointment |
| appointment_time | TIME | NO | Scheduled time of the appointment |
| appointment_type | VARCHAR(100) | NO | Type of visit (New Patient Visit, Follow-up Visit, Annual Physical, Sick Visit, Procedure, Consultation, Telehealth, Urgent Care) |
| status | VARCHAR(50) | NO | Current status (Scheduled, Checked-In, In Progress, Completed, Cancelled, No-Show) |
| chief_complaint | TEXT | YES | Primary reason for the visit as stated by the patient |
| visit_reason | TEXT | YES | Clinical reason for the visit |
| duration_minutes | INTEGER | YES | Scheduled duration of appointment in minutes (typically 15, 30, 45, or 60) |
| copay_collected | DECIMAL(10,2) | YES | Copayment amount collected in USD |
| checked_in_time | TIMESTAMP | YES | Actual time when patient checked in for the appointment |
| checked_out_time | TIMESTAMP | YES | Actual time when patient checked out after the appointment |
| created_date | TIMESTAMP | YES | Date and time when the appointment was created |

#### Relationships:
- References `patients.patient_id` (Many-to-One: Multiple appointments for one patient)
- References `providers.provider_id` (Many-to-One: Multiple appointments for one provider)
- References `facilities.facility_id` (Many-to-One: Multiple appointments at one facility)
- Referenced by `diagnoses.appointment_id` (One-to-Many: One appointment can result in multiple diagnoses)
- Referenced by `prescriptions.appointment_id` (One-to-Many: One appointment can generate multiple prescriptions)
- Referenced by `lab_results.appointment_id` (One-to-Many: One appointment can order multiple lab tests)

---

### 6. diagnoses

Records all diagnoses made during patient encounters.

**Table Name:** `diagnoses`  
**Primary Key:** `diagnosis_id`  
**Foreign Keys:** `appointment_id`, `patient_id`, `provider_id`

#### Columns:

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|-------------|
| diagnosis_id | VARCHAR(20) | NO | Primary key. Unique identifier for each diagnosis (Format: DIA######) |
| appointment_id | VARCHAR(20) | NO | Foreign key referencing appointments.appointment_id |
| patient_id | VARCHAR(20) | NO | Foreign key referencing patients.patient_id |
| provider_id | VARCHAR(20) | NO | Foreign key referencing providers.provider_id who made the diagnosis |
| icd10_code | VARCHAR(10) | NO | ICD-10 diagnosis code (International Classification of Diseases, 10th Revision) |
| diagnosis_description | TEXT | NO | Full text description of the diagnosis |
| diagnosis_type | VARCHAR(50) | NO | Classification of diagnosis (Primary, Secondary, Tertiary) |
| severity | VARCHAR(20) | YES | Severity level (Mild, Moderate, Severe) |
| onset_date | DATE | YES | Date when the condition first began (if known) |
| status | VARCHAR(50) | YES | Current status of the diagnosis (Active, Resolved, Chronic, Recurrent) |
| notes | TEXT | YES | Additional clinical notes about the diagnosis |
| created_date | TIMESTAMP | YES | Date and time when the diagnosis was recorded |

#### Relationships:
- References `appointments.appointment_id` (Many-to-One: Multiple diagnoses can be made in one appointment)
- References `patients.patient_id` (Many-to-One: Multiple diagnoses for one patient)
- References `providers.provider_id` (Many-to-One: Multiple diagnoses by one provider)

#### Common ICD-10 Codes in Dataset:
- **E11.9** - Type 2 diabetes mellitus without complications
- **I10** - Essential (primary) hypertension
- **J45.909** - Unspecified asthma, uncomplicated
- **E78.5** - Hyperlipidemia, unspecified
- **F41.9** - Anxiety disorder, unspecified
- **M54.5** - Low back pain
- **N39.0** - Urinary tract infection, site not specified
- **R51** - Headache

---

### 7. prescriptions

Stores all medication prescriptions written for patients.

**Table Name:** `prescriptions`  
**Primary Key:** `prescription_id`  
**Foreign Keys:** `appointment_id`, `patient_id`, `provider_id`

#### Columns:

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|-------------|
| prescription_id | VARCHAR(20) | NO | Primary key. Unique identifier for each prescription (Format: RX#######) |
| appointment_id | VARCHAR(20) | NO | Foreign key referencing appointments.appointment_id |
| patient_id | VARCHAR(20) | NO | Foreign key referencing patients.patient_id |
| provider_id | VARCHAR(20) | NO | Foreign key referencing providers.provider_id who prescribed the medication |
| medication_name | VARCHAR(200) | NO | Brand or common name of the medication |
| generic_name | VARCHAR(200) | YES | Generic/chemical name of the medication |
| dosage | VARCHAR(100) | NO | Strength and dosage form (e.g., "500mg", "10mg tablet") |
| frequency | VARCHAR(100) | NO | How often to take the medication (e.g., "Twice daily", "Once daily at bedtime") |
| route | VARCHAR(50) | YES | Route of administration (Oral, Inhalation, Topical, Injection) |
| quantity | INTEGER | YES | Total quantity prescribed |
| refills_allowed | INTEGER | YES | Number of refills authorized (0 = no refills) |
| days_supply | INTEGER | YES | Number of days the prescription should last (typically 30, 60, or 90) |
| prescription_date | DATE | NO | Date when the prescription was written |
| start_date | DATE | YES | Date when patient should start taking medication |
| end_date | DATE | YES | Date when patient should stop taking medication (if applicable) |
| pharmacy_name | VARCHAR(200) | YES | Pharmacy where prescription was sent |
| status | VARCHAR(50) | YES | Current status (Active, Completed, Discontinued, On Hold) |
| is_controlled_substance | BOOLEAN | YES | Indicates if medication is a controlled substance requiring special handling |
| notes | TEXT | YES | Special instructions or notes (e.g., "Take with food", "May cause drowsiness") |
| created_date | TIMESTAMP | YES | Date and time when the prescription was created |

#### Relationships:
- References `appointments.appointment_id` (Many-to-One: Multiple prescriptions can be written during one appointment)
- References `patients.patient_id` (Many-to-One: Multiple prescriptions for one patient)
- References `providers.provider_id` (Many-to-One: Multiple prescriptions by one provider)

#### Common Medications in Dataset:
- **Metformin** - Type 2 diabetes management
- **Lisinopril** - Hypertension treatment
- **Atorvastatin** - Cholesterol management
- **Omeprazole** - Acid reflux/GERD treatment
- **Albuterol** - Asthma/bronchospasm relief

---

### 8. lab_results

Contains laboratory test results and diagnostic data.

**Table Name:** `lab_results`  
**Primary Key:** `result_id`  
**Foreign Keys:** `appointment_id`, `patient_id`, `provider_id`

#### Columns:

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|-------------|
| result_id | VARCHAR(20) | NO | Primary key. Unique identifier for each lab result (Format: LAB#######) |
| appointment_id | VARCHAR(20) | YES | Foreign key referencing appointments.appointment_id (NULL for standalone lab orders) |
| patient_id | VARCHAR(20) | NO | Foreign key referencing patients.patient_id |
| provider_id | VARCHAR(20) | NO | Foreign key referencing providers.provider_id who ordered the test |
| test_name | VARCHAR(200) | NO | Full name of the laboratory test |
| test_code | VARCHAR(50) | YES | Standardized test code (e.g., CPT code or local lab code) |
| test_category | VARCHAR(100) | YES | Category of test (Hematology, Chemistry, Endocrinology, Immunology, Urinalysis, Coagulation, Cardiac, Tumor Marker) |
| result_value | VARCHAR(200) | YES | Actual result value (can be numeric or text) |
| unit_of_measure | VARCHAR(50) | YES | Unit of measurement for the result (e.g., mg/dL, mEq/L, %) |
| reference_range | VARCHAR(100) | YES | Normal reference range for interpretation |
| abnormal_flag | VARCHAR(20) | YES | Indicator if result is outside normal range (Normal, High, Low, Critical) |
| status | VARCHAR(50) | YES | Result status (Final, Preliminary, Pending, Corrected) |
| specimen_type | VARCHAR(100) | YES | Type of specimen collected (Blood, Urine, Serum, Plasma, Whole Blood) |
| collection_date | TIMESTAMP | YES | Date and time when specimen was collected |
| result_date | TIMESTAMP | YES | Date and time when result was finalized |
| performing_lab | VARCHAR(200) | YES | Name of laboratory that performed the test (Quest Diagnostics, LabCorp, Mayo Clinic Laboratories, etc.) |
| notes | TEXT | YES | Additional notes (e.g., "Fasting specimen", "Critical value called to provider") |
| created_date | TIMESTAMP | YES | Date and time when the result was entered into system |

#### Relationships:
- References `appointments.appointment_id` (Many-to-One: Multiple lab results can be ordered from one appointment)
- References `patients.patient_id` (Many-to-One: Multiple lab results for one patient)
- References `providers.provider_id` (Many-to-One: Multiple lab results ordered by one provider)

#### Common Lab Tests in Dataset:
- **CBC** (Complete Blood Count) - Hematology panel
- **HbA1c** (Hemoglobin A1C) - Diabetes monitoring
- **BMP** (Basic Metabolic Panel) - Chemistry panel
- **Lipid Panel** - Cholesterol and triglycerides
- **TSH** (Thyroid Stimulating Hormone) - Thyroid function
- **Urinalysis** - Kidney and urinary tract health

---

## Table Relationships Summary

```
facilities (1) ----< providers (M)
facilities (1) ----< appointments (M)

insurance_plans (1) ----< patients (M) [primary_insurance_id]
insurance_plans (1) ----< patients (M) [secondary_insurance_id]

patients (1) ----< appointments (M)
patients (1) ----< diagnoses (M)
patients (1) ----< prescriptions (M)
patients (1) ----< lab_results (M)

providers (1) ----< appointments (M)
providers (1) ----< diagnoses (M)
providers (1) ----< prescriptions (M)
providers (1) ----< lab_results (M)

appointments (1) ----< diagnoses (M)
appointments (1) ----< prescriptions (M)
appointments (1) ----< lab_results (M)
```

**Legend:**
- `(1)` = One
- `(M)` = Many
- `----<` = One-to-Many relationship

---

## Sample SQL Queries for Text-to-SQL Testing

### Basic Queries

1. **Find all active patients**
```sql
SELECT patient_id, first_name, last_name, date_of_birth, phone
FROM patients
WHERE is_active = TRUE;
```

2. **List all providers by specialty**
```sql
SELECT provider_id, first_name, last_name, specialty, facility_id
FROM providers
WHERE specialty = 'Cardiology'
AND is_active = TRUE;
```

3. **Get upcoming appointments**
```sql
SELECT appointment_id, patient_id, provider_id, appointment_date, appointment_time, status
FROM appointments
WHERE appointment_date >= CURRENT_DATE
AND status = 'Scheduled'
ORDER BY appointment_date, appointment_time;
```

### Intermediate Queries

4. **Find patients with diabetes diagnoses**
```sql
SELECT DISTINCT p.patient_id, p.first_name, p.last_name, d.diagnosis_description
FROM patients p
JOIN diagnoses d ON p.patient_id = d.patient_id
WHERE d.icd10_code LIKE 'E11%'
AND d.status = 'Active';
```

5. **Count appointments by provider**
```sql
SELECT pr.provider_id, pr.first_name, pr.last_name, COUNT(a.appointment_id) as total_appointments
FROM providers pr
LEFT JOIN appointments a ON pr.provider_id = a.provider_id
GROUP BY pr.provider_id, pr.first_name, pr.last_name
ORDER BY total_appointments DESC;
```

6. **List active prescriptions for a specific patient**
```sql
SELECT prescription_id, medication_name, dosage, frequency, prescription_date, refills_allowed
FROM prescriptions
WHERE patient_id = 'PAT000001'
AND status = 'Active'
ORDER BY prescription_date DESC;
```

### Advanced Queries

7. **Find patients with abnormal lab results**
```sql
SELECT DISTINCT p.patient_id, p.first_name, p.last_name, 
       l.test_name, l.result_value, l.abnormal_flag
FROM patients p
JOIN lab_results l ON p.patient_id = l.patient_id
WHERE l.abnormal_flag IN ('High', 'Low', 'Critical')
AND l.status = 'Final'
ORDER BY l.abnormal_flag, p.last_name;
```

8. **Calculate average appointment duration by type**
```sql
SELECT appointment_type, 
       AVG(duration_minutes) as avg_duration,
       COUNT(*) as total_appointments
FROM appointments
WHERE status = 'Completed'
GROUP BY appointment_type
ORDER BY avg_duration DESC;
```

9. **Find providers with the most diagnoses in the last 6 months**
```sql
SELECT pr.provider_id, pr.first_name, pr.last_name, pr.specialty,
       COUNT(d.diagnosis_id) as diagnosis_count
FROM providers pr
JOIN diagnoses d ON pr.provider_id = d.provider_id
WHERE d.created_date >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY pr.provider_id, pr.first_name, pr.last_name, pr.specialty
ORDER BY diagnosis_count DESC
LIMIT 10;
```

10. **Patient visit summary with diagnoses and prescriptions**
```sql
SELECT a.appointment_id, a.appointment_date,
       p.first_name || ' ' || p.last_name as patient_name,
       pr.first_name || ' ' || pr.last_name as provider_name,
       a.chief_complaint,
       STRING_AGG(DISTINCT d.diagnosis_description, '; ') as diagnoses,
       STRING_AGG(DISTINCT rx.medication_name, '; ') as medications
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN providers pr ON a.provider_id = pr.provider_id
LEFT JOIN diagnoses d ON a.appointment_id = d.appointment_id
LEFT JOIN prescriptions rx ON a.appointment_id = rx.appointment_id
WHERE a.status = 'Completed'
GROUP BY a.appointment_id, a.appointment_date, p.first_name, p.last_name, 
         pr.first_name, pr.last_name, a.chief_complaint
ORDER BY a.appointment_date DESC
LIMIT 20;
```

---

## Data Quality Notes

- All ID fields follow consistent formatting patterns (FAC######, INS######, PAT######, etc.)
- Phone numbers use consistent format: 555-XXX-XXXX
- Dates are stored in ISO format (YYYY-MM-DD)
- Foreign key relationships are maintained across all tables
- Approximately 5-10% of records include NULL values where appropriate to simulate real-world data
- Boolean fields use TRUE/FALSE values
- Timestamp fields include date and time components

---

## Usage Instructions

### Loading CSV Files into PostgreSQL

```sql
-- Create database
CREATE DATABASE wrs_health_ehr;

-- Connect to database
\c wrs_health_ehr

-- Create tables (use SQL schema provided separately)

-- Load CSV files
\COPY facilities FROM 'facilities.csv' CSV HEADER;
\COPY insurance_plans FROM 'insurance_plans.csv' CSV HEADER;
\COPY patients FROM 'patients.csv' CSV HEADER;
\COPY providers FROM 'providers.csv' CSV HEADER;
\COPY appointments FROM 'appointments.csv' CSV HEADER;
\COPY diagnoses FROM 'diagnoses.csv' CSV HEADER;
\COPY prescriptions FROM 'prescriptions.csv' CSV HEADER;
\COPY lab_results FROM 'lab_results.csv' CSV HEADER;
```

### Verifying Data Load

```sql
-- Check record counts
SELECT 'facilities' as table_name, COUNT(*) as record_count FROM facilities
UNION ALL
SELECT 'insurance_plans', COUNT(*) FROM insurance_plans
UNION ALL
SELECT 'patients', COUNT(*) FROM patients
UNION ALL
SELECT 'providers', COUNT(*) FROM providers
UNION ALL
SELECT 'appointments', COUNT(*) FROM appointments
UNION ALL
SELECT 'diagnoses', COUNT(*) FROM diagnoses
UNION ALL
SELECT 'prescriptions', COUNT(*) FROM prescriptions
UNION ALL
SELECT 'lab_results', COUNT(*) FROM lab_results;
```

---

## Best Practices for Text-to-SQL Applications

1. **Always specify table aliases** for clarity in JOIN operations
2. **Use appropriate WHERE clauses** to filter on status fields (is_active, status)
3. **Consider date ranges** when querying time-sensitive data
4. **Join on proper foreign keys** as documented in the relationships section
5. **Aggregate carefully** using GROUP BY when counting or summarizing
6. **Handle NULL values** appropriately in WHERE clauses and calculations
7. **Use DISTINCT** when necessary to avoid duplicate results from JOINs
8. **Limit result sets** for performance when appropriate

---

## Contact & Support

For questions about this database schema or sample data:
- Review the WRS Health EHR User Guide documentation
- Contact database administration team
- Reference this documentation for table structures and relationships