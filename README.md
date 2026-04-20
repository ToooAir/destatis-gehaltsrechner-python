# README — Destatis Gehaltsvergleich Python Salary Estimator

[👉 繁體中文版說明 (Traditional Chinese Version)](README_TC.md)

> **⚠️ Disclaimer**  
> This project is an unofficial tool. The model coefficients and calculation logic used are extracted from the frontend code (`app.js`) of the salary comparison tool published by the Federal Statistical Office of Germany (Destatis). They were not obtained via an official API or an officially authorized package. The estimation results are for reference only. Actual salaries are affected by market fluctuations, personal negotiation skills, and other unmeasured variables. This project bears no legal responsibility for the accuracy or applicability of the calculation results.

***

## Table of Contents

1. [Project Description](#1-project-description)
2. [Quick Start](#2-quick-start)
3. [Parameter Details](#3-parameter-details)
    - [berufsjahre — Years of Professional Experience](#31-berufsjahre--years-of-professional-experience)
    - [ausbildungsjahre — Years of Education](#32-ausbildungsjahre--years-of-education)
    - [ef59u3_key — Weekly Working Hours Group](#33-ef59u3_key--weekly-working-hours-group)
    - [unternehmen_key — Company Size](#34-unternehmen_key--company-size)
    - [bundesland_key — Federal State](#35-bundesland_key--federal-state)
    - [kldb_code — Occupation Code (KldB 2010)](#36-kldb_code--occupation-code-kldb-2010)
    - [vollzeit — Full-time/Part-time](#37-vollzeit--full-timepart-time)
    - [geschlecht — Model Selection (Gender)](#38-geschlecht--model-selection-gender)
    - [befristet — Contract Type](#39-befristet--contract-type)
4. [KldB Full Occupation Code List](#4-kldb-full-occupation-code-list)
5. [Model Principles](#5-model-principles)
6. [Usage Examples](#6-usage-examples)
7. [Important Notes](#7-important-notes)

***

## 1. Project Description

Based on the [Gehaltsvergleich](https://service.destatis.de/DE/gehaltsvergleich/) (Salary Comparison) published by the Federal Statistical Office of Germany (Destatis), this tool translates the **OLS log-linear regression model** from its frontend `app.js` into Python. It estimates the **median gross monthly salary (Bruttogehalt Median)** in Germany.

```
File Structure:
destatis-gehaltsrechner-python/
├── salary_calculator/
│   ├── coefficients.json     ← All regression coefficients (extracted from app.js)
│   └── __init__.py           ← Main calculation script
├── README.md                 ← This documentation (English)
└── README_TC.md              ← Traditional Chinese documentation
```

***

## 2. Quick Start

```python
from salary_calculator import load_models, schaetze_monatsgehalt, formatiere_ergebnis

MODELS = load_models("coefficients.json")

result = schaetze_monatsgehalt(
    berufsjahre=5,
    ausbildungsjahre=19,
    ef59u3_key="EF59U3_15",
    unternehmen_key="UNGr_UN6",
    bundesland_key="EF13_101",
    kldb_code="434",
    vollzeit=True,
    geschlecht="maenner",
    befristet=False,
    models=MODELS,
)
print(formatiere_ergebnis(result))
```

***

## 3. Parameter Details

***

### 3.1 `berufsjahre` — Years of Professional Experience

**Type:** `float`
**Range:** `0` to `51` (years)
**Description:** Total years of working experience in the same field or profession, NOT absolute age.

```python
berufsjahre = 5    # 5 years of experience
berufsjahre = 0    # Entry-level / Fresh graduate
berufsjahre = 20   # Senior staff
```

> **Note:** Salary benefits do not grow linearly. The model uses a quadratic function (including a negative coefficient `BE_quad` for squared experience), reflecting the reality that the marginal benefit of a raise decreases as seniority increases.

***

### 3.2 `ausbildungsjahre` — Years of Education

**Type:** `float`
**Description:** Total years of formal education from primary school to the highest degree completed.

| Education Level | Years | Description |
| :-- | :-- | :-- |
| No formal qualifications | 9 | Compulsory education only (Hauptschule) |
| Hauptschulabschluss + Training | 12 | Middle school + Ausbildung |
| Mittlere Reife + Training | 13 | Secondary school + Ausbildung |
| Abitur (High school diploma) | 13 | Not including university |
| Abitur + Ausbildung (Dual) | 15 | High school + Vocational training |
| Bachelor (3 years) | 16 | 13 years of school + 3 years of uni |
| Bachelor (4 years) | 17 | 13 years of school + 4 years of uni |
| Master / Diplom | 18–19 | 13 years of school + 5–6 years of uni |
| Staatsexamen (Law/Medicine) | 19–20 | Includes internship year |
| Promotion (PhD) | 21–23 | Includes PhD duration |

```python
ausbildungsjahre = 19   # Master's degree
ausbildungsjahre = 17   # Bachelor's degree
ausbildungsjahre = 13   # Vocational training (Ausbildung)
```

***

### 3.3 `ef59u3_key` — Weekly Working Hours Group

**Type:** `str`
**Description:** Choose the bracket that best matches your **actual weekly working hours**.

| Parameter Value | Weekly Hours | Typical Scenario | Salary Impact (vs 21–32h) |
| :-- | :-- | :-- | :-- |
| `"EF59U3_11"` | ≤ 20 hours | Minor part-time | −5.7% |
| `"EF59U3_12"` | 21–32 hours | Standard part-time (**Reference Group**) | ± 0% |
| `"EF59U3_13"` | 33–36 hours | Reduced full-time (Teilzeit) | +10.1% |
| `"EF59U3_14"` | 37–39 hours | TVöD Public Sector Standard | +11.5% |
| `"EF59U3_15"` | 40 hours | Standard private sector full-time | +21.6% |
| `"EF59U3_16"` | ≥ 41 hours | Overtime / high hours | +30.2% |

```python
ef59u3_key = "EF59U3_15"   # Standard full-time, 40 hours/week
ef59u3_key = "EF59U3_14"   # Civil servant / TVöD, 38.5 hours/week
```

> **Important:** This parameter also affects the baseline calculation for experience benefits. The longer the weekly hours, the slightly different the salary growth brought by seniority.

***

### 3.4 `unternehmen_key` — Company Size

**Type:** `str`
**Description:** Select based on the **total number of employees** in the entire company. Larger companies generally pay higher salaries.

| Parameter Value | Employee Count | Coefficient | vs Large Enterprise |
| :-- | :-- | :-- | :-- |
| `"UNGr_UN1"` | 1–9 | −0.176 | ~ **16%** less |
| `"UNGr_UN2"` | 10–49 | −0.108 | ~ **10%** less |
| `"UNGr_UN3"` | 50–249 | −0.070 | ~ **7%** less |
| `"UNGr_UN4"` | 250–499 | −0.042 | ~ **4%** less |
| `"UNGr_UN5"` | 500–999 | −0.026 | ~ **3%** less |
| `"UNGr_UN6"` | ≥ 1000 | 0 (**Reference**) | Baseline |

```python
unternehmen_key = "UNGr_UN6"   # Large enterprise (e.g., SAP, Deutsche Bahn)
unternehmen_key = "UNGr_UN3"   # Medium enterprise (50–249 people)
unternehmen_key = "UNGr_UN2"   # Small company (10–49 people)
```

***

### 3.5 `bundesland_key` — Federal State

**Type:** `str`
**Description:** The German federal state where you work. The reference group is **NRW (`EF13_105`)**, with a coefficient of 0.

| Parameter Value | Federal State | Coefficient | Region |
| :-- | :-- | :-- | :-- |
| `"EF13_101"` | Schleswig-Holstein | −0.015 | North |
| `"EF13_102"` | Hamburg | +0.031 | North |
| `"EF13_103"` | Niedersachsen | −0.001 | North |
| `"EF13_104"` | Bremen | −0.003 | North |
| `"EF13_105"` | Nordrhein-Westfalen | 0 (**Reference**) | West |
| `"EF13_106"` | Hessen | +0.029 | West |
| `"EF13_107"` | Rheinland-Pfalz | −0.003 | West |
| `"EF13_108"` | Baden-Württemberg | +0.052 | South ⬆ |
| `"EF13_109"` | Bayern | +0.034 | South ⬆ |
| `"EF13_110"` | Saarland | −0.002 | Southwest |
| `"EF13_111"` | Berlin | −0.011 | East/Capital |
| `"EF13_112"` | Brandenburg | −0.084 | East |
| `"EF13_113"` | Mecklenburg-Vorpommern | −0.094 | East |
| `"EF13_114"` | Sachsen | −0.114 | East ⬇ |
| `"EF13_115"` | Sachsen-Anhalt | −0.103 | East ⬇ |
| `"EF13_116"` | Thüringen | −0.103 | East ⬇ |

```python
bundesland_key = "EF13_101"   # Schleswig-Holstein
bundesland_key = "EF13_102"   # Hamburg
bundesland_key = "EF13_108"   # Baden-Württemberg (Highest paying state)
```

> The East-West salary divide is obvious: Eastern states are generally **8–11%** lower, while the Southwest (BW/Bayern) is **3–5%** higher.

***

### 3.6 `kldb_code` — Occupation Code (KldB 2010)

**Type:** `str` (3-digit string)
**Description:** Use the three-digit code of the German **Classification of Occupations (KldB 2010)**. This is the single parameter that affects salary the most.

#### Code Structure

```
Code Format:  X  Y  Z
              │  │  └── Last digit: Skill Level (Anforderungsniveau)
              │  └───── Middle digit: Occupation Group (Berufsgruppe)
              └──────── First digit: Major Occupation Group (Berufshauptgruppe)
```

#### Last Digit Z — Skill Level (Crucial!)

| Last Digit | Skill Level | Corresponding Education | Description |
| :-- | :-- | :-- | :-- |
| `1` | Helfer / Anlernkräfte | No special education | Assistant, trainee |
| `2` | Fachkräfte | Vocational training (Ausbildung) | Qualified skilled worker |
| `3` | Spezialist/innen | Meister / Techniker / FH | Advanced tech/admin |
| `4` | Expert/innen | Bachelor's degree or above | Engineer, academic role |

> **If the second-to-last digit is `9`**, it indicates a **Managerial Role (Führungskraft)**. The model will add the `Lead1` coefficient (approx. +8–9%). Example: `439` = IT Manager.

***

## 4. KldB Full Occupation Code List

For exact occupation codes, you can search the official website: [klassifikationsserver.de](https://www.klassifikationsserver.de/klassService/thyme/variant/kldb2010)

*(Due to length, primary categories are listed below. For detailed IT roles, see the Chinese README or official KldB)*

- **01–12**: Agriculture, Forestry, Horticulture
- **21–29**: Mining, Chemistry, Metals, Machinery, Electronics
- **31–34**: Construction and Building Services
- **41–43**: Information Technology, Natural Sciences (Includes `434x` Software Engineering)
- **51–54**: Transport, Logistics
- **61–63**: Commerce, Retail, Tourism
- **71–73**: Business Management, Marketing, Media
- **81–84**: Healthcare, Social Work, Education
- **91–94**: Law, Finance, Administration, Arts

***

### 3.7 `vollzeit` — Full-time/Part-time

**Type:** `bool`
**Description:** Whether the employment is full-time.

| Value | Description | Salary Impact |
| :-- | :-- | :-- |
| `True` | Full-time (Vollzeit) — Reference | ± 0% |
| `False` | Part-time (Teilzeit) | Approx. −5.2% |

```python
vollzeit = True    # Full-time
vollzeit = False   # Part-time (combines with EF59U3_11 or EF59U3_12)
```

***

### 3.8 `geschlecht` — Model Selection (Gender)

**Type:** `str`
**Description:** Chooses which regression model to use. The coefficients vary slightly across the three models.

| Value | Model | Intercept | Description |
| :-- | :-- | :-- | :-- |
| `"gesamt"` | Overall Average | 7.7281 | Mixed data, includes GPG field (but doesn't actively apply it) |
| `"maenner"` | Men | 7.8486 | Men-only regression, higher intercept |
| `"frauen"` | Women | 7.7281 | Same base as 'gesamt' but dynamically applies the GPG coefficient (−8%) |

```python
geschlecht = "maenner"   # Estimate for men
geschlecht = "frauen"    # Estimate for women (applies −8% GPG)
geschlecht = "gesamt"    # Overall average (neutral estimate)
```

> **GPG (Gender Pay Gap) Coefficient:** −0.0805 in the `gesamt` model, and −0.0848 in the `maenner` model. The women's model incorporates this coefficient into the linear predictor to reflect the real-world gender pay gap in Germany.

***

### 3.9 `befristet` — Contract Type

**Type:** `bool`
**Description:** Whether it's a fixed-term contract (Befristeter Arbeitsvertrag).

| Value | Description | Salary Impact |
| :-- | :-- | :-- |
| `False` | Unlimited (Unbefristet) — Reference | ± 0% |
| `True` | Fixed-term / Temporary (Befristet) | Approx. −7.5% |

```python
befristet = False   # Permanent contract
befristet = True    # Probation period / temp / fixed-term contract
```

***

## 5. Model Principles

This tool uses **OLS log-linear regression**:

$\ln(\text{Monthly Salary}) = \text{Intercept} + \beta_{\text{BE}} \cdot f(\text{Experience}) + \beta_{\text{EF40}} \cdot g(\text{Edu}) + \sum_i \beta_i \cdot \mathbf{1}[\text{Category}_i]$

$\text{Monthly Salary (Median)} = e^{\hat{y}}$

Coefficients are derived from the OLS estimation results in Destatis's official `app.js`, which implies calculations from the German Structure of Earnings Survey (Verdienststrukturerhebung). The output is the **median gross monthly salary (Bruttogehalt Median)**, not the mean.

***

## 6. Usage Examples

```python
MODELS = load_models("coefficients.json")

# Backend Engineer, Hamburg, Master's, 10 years, Large Enterprise, Full-time, Permanent
result = schaetze_monatsgehalt(
    berufsjahre=10,
    ausbildungsjahre=19,        # Master's
    ef59u3_key="EF59U3_15",     # 40 hours/week
    unternehmen_key="UNGr_UN6", # ≥1000 employees
    bundesland_key="EF13_102",  # Hamburg
    kldb_code="43414",          # Software Developer
    vollzeit=True,
    geschlecht="maenner",
    befristet=False,
    models=MODELS,
)

# IT Manager, Bayern, Master's, 15 years, Large Enterprise
result2 = schaetze_monatsgehalt(
    berufsjahre=15,
    ausbildungsjahre=19,
    ef59u3_key="EF59U3_16",     # >40 hours/week
    unternehmen_key="UNGr_UN6",
    bundesland_key="EF13_109",  # Bayern
    kldb_code="43394",          # IT Manager (Ends with 4, second-to-last 9 = Management)
    vollzeit=True,
    geschlecht="maenner",
    befristet=False,
    models=MODELS,
)
```

***

## 7. Important Notes

- Outputs are in **Gross (Brutto)** monthly salary. To find net pay (Netto), use standard calculators evaluating your tax class (Steuerklasse) and social security.
- The results represent the **median estimate**, and are not guaranteed salaries.
- The model baseline year mirrors the Destatis release year (around the 2018–2020 Structure of Earnings Survey), and does not account for recent inflation adjustments.
- If unsure about your occupation code, search your job title on the [Klassifikationsserver](https://www.klassifikationsserver.de/klassService/thyme/variant/kldb2010).
