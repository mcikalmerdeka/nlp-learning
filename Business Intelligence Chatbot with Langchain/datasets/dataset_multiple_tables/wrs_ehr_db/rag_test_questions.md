## Basic Queries (Simple SELECT with WHERE)

1. "Show me all active patients in Texas"
2. "List all cardiologists who are accepting new patients"
3. "What are the upcoming appointments for tomorrow?"
4. "Find all patients with blood type O negative"
5. "Show me all cancelled appointments in the last 30 days"
6. "List all HMO insurance plans that are currently active"
7. "Which facilities are located in California?"
8. "Show me all prescriptions for Metformin"
9. "Find all lab results with critical abnormal flags"
10. "What are the completed appointments for patient PAT000001?"

## Intermediate Queries (JOINs and Aggregations)

11. "How many appointments does each provider have this month?"
12. "What is the average copay amount collected by appointment type?"
13. "Show me the total number of patients per insurance company"
14. "Which providers have written the most prescriptions in 2024?"
15. "What are the top 5 most common diagnoses across all patients?"
16. "How many appointments were no-shows by facility?"
17. "What is the distribution of patients by age group?"
18. "Show me the average number of refills allowed by medication type"
19. "Which facilities have the most providers on staff?"
20. "What percentage of appointments result in a prescription being written?"

## Advanced Queries (Multiple JOINs, Subqueries, Complex Logic)

21. "Show me patients who have both diabetes (E11.9) and hypertension (I10) diagnoses"
22. "What is the average time between appointment check-in and check-out by provider?"
23. "Find patients who have had more than 5 appointments in the last 6 months"
24. "Which providers have the highest patient satisfaction based on completed appointments?"
25. "Show me the month-over-month growth in new patient registrations for each year"
26. "What are the most frequently prescribed medications for patients with diabetes?"
27. "Find all patients who have abnormal lab results but no follow-up appointment scheduled"
28. "What is the average number of diagnoses per appointment by specialty?"
29. "Show me the revenue (copay collected) by facility for each quarter"
30. "Which insurance plans have the highest average out-of-pocket costs for patients?"

## Healthcare-Specific Analytics

31. "What is the average days supply for controlled substance prescriptions versus non-controlled?"
32. "Show me the distribution of appointment types by provider specialty"
33. "Find patients with chronic conditions (status = 'Chronic') who haven't had an appointment in 90 days"
34. "What percentage of lab results are returned as abnormal by test category?"
35. "Which facilities have the longest average appointment duration?"
36. "Show me the top 10 ICD-10 codes diagnosed in urgent care settings"
37. "What is the prescription refill rate by medication category?"
38. "Find providers who have ordered the most lab tests per patient encounter"
39. "What is the patient retention rate by primary care provider over the last year?"
40. "Show me the correlation between appointment duration and number of diagnoses made"

## Time-Series and Trend Analysis

41. "What is the monthly trend of new patient registrations over the past 2 years?"
42. "Show me the year-over-year growth in total appointments by specialty"
43. "What are the peak hours for appointment scheduling across all facilities?"
44. "Display the quarterly trend of average copay amounts collected"
45. "How has the prescription volume changed month-over-month for the top 5 medications?"
46. "What is the seasonal pattern of flu-related diagnoses (J06.9)?"
47. "Show me the trend of telehealth appointments versus in-person visits by month"
48. "What is the weekly distribution of lab test orders throughout the year?"

## Patient Journey and Clinical Workflow

49. "Show me the complete patient journey for patient PAT000001 including all appointments, diagnoses, prescriptions, and lab results"
50. "Find patients who received a diagnosis but didn't get a prescription during the same visit"
51. "What is the average time between a lab order and result availability?"
52. "Show me patients who have multiple active prescriptions from different providers"
53. "Which diagnoses most commonly lead to lab test orders?"
54. "Find appointment patterns for patients with recurring visits (3+ visits in 6 months)"
55. "What percentage of new patient visits result in a follow-up appointment being scheduled?"

## Financial and Operational Metrics

56. "What is the total revenue collected from copayments by insurance plan type?"
57. "Show me the appointment no-show rate by day of the week"
58. "What is the average patient load per provider by specialty?"
59. "Calculate the utilization rate of each facility based on appointment volume"
60. "Which providers have the highest percentage of completed appointments?"
61. "What is the average cost of prescriptions (quantity × days_supply) by pharmacy?"
62. "Show me the distribution of appointment durations and their impact on provider schedules"

## Population Health and Quality Metrics

63. "How many patients have uncontrolled diabetes (HbA1c > 7%) based on lab results?"
64. "Find patients due for annual physical exams (last physical > 12 months ago)"
65. "What percentage of hypertensive patients have had their blood pressure checked in the last 3 months?"
66. "Show me patients with active prescriptions who haven't had a follow-up appointment"
67. "Which patients are on 5 or more concurrent medications (polypharmacy)?"
68. "Find gaps in care: patients with chronic conditions but no appointments in 6 months"
69. "What is the prevalence of common chronic conditions by age group and gender?"
70. "Show me vaccination rates by patient demographics"

## Provider Performance and Comparison

71. "Compare the average number of diagnoses per visit across different specialties"
72. "Which providers have the shortest average wait time (checked-in to appointment time)?"
73. "Show me provider productivity: appointments completed per week by specialty"
74. "Find providers with the highest prescription-to-visit ratio"
75. "What is the distribution of patient complexity (number of active diagnoses) by provider?"

## Complex Multi-Table Analytics

76. "Show me facilities with the highest patient satisfaction based on completed visits and return rates"
77. "What is the medication adherence rate based on prescription refills versus days supply?"
78. "Find patients who have switched primary care providers in the last year"
79. "Show me the most common diagnosis-prescription pairs across all encounters"
80. "What is the average patient age by insurance plan type and how does it affect visit frequency?"
