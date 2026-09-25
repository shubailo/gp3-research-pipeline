# SEARCH-hypothermia-lmic: Meta-analysis Search Strategy

This document contains the formalized search strings and keys for the meta-analysis on Therapeutic Hypothermia in LMICs post-HELIX.

## 1. PubMed / MEDLINE Search String

### [Block A] Condition: Neonatal Encephalopathy / HIE
```
("Asphyxia Neonatorum"[Mesh] OR "Hypoxia-Ischemia, Brain"[Mesh] OR "Infant, Newborn, Diseases"[Mesh] OR "neonatal encephalopathy" OR "hypoxic ischemic encephalopathy" OR "HIE" OR "perinatal asphyxia" OR "birth asphyxia" OR "hypoxic-ischemic encephalopathy")
```

### [Block B] Intervention: Therapeutic Hypothermia
```
("Hypothermia, Induced"[Mesh] OR "therapeutic hypothermia" OR "body temperature management" OR "cooling" OR "head cooling" OR "whole body cooling" OR "cold therapy")
```

### [Block C] Setting: Low and Middle-Income Countries (LMIC Filter)
*Derived from Cochrane EPOC (2023) and World Bank Classifications.*
```
("Developing Countries"[Mesh] OR "Low-Income Population"[Mesh] OR "developing country" OR "developing countries" OR "low income country" OR "low income countries" OR "middle income country" OR "middle income countries" OR "LMIC" OR "low-resource setting" OR "resource limited setting" OR "Africa" OR "Asia" OR "South America" OR "Latin America" OR "Central America" OR "transitional countries" OR "underdeveloped countries")
```

### [Combined] Master PubMed String (High Sensitivity)
```
(("Asphyxia Neonatorum"[Mesh] OR "Hypoxia-Ischemia, Brain"[Mesh] OR "neonatal encephalopathy" OR "hypoxic ischemic encephalopathy" OR "HIE" OR "perinatal asphyxia" OR "birth asphyxia") AND ("Hypothermia, Induced"[Mesh] OR "therapeutic hypothermia" OR "body temperature management" OR "cooling") AND ("Developing Countries"[Mesh] OR "Low-Income Population"[Mesh] OR "developing countries" OR "low income countries" OR "middle income countries" OR "LMIC" OR "low-resource setting" OR "resource-limited setting" OR "Africa"[Mesh] OR "Asia"[Mesh] OR "South America"[Mesh] OR "Latin America"[Mesh] OR "Central America"[Mesh]))
```

---

## 2. Embase Search Strategy

### [Block A] Condition
```
('asphyxia neonatorum'/exp OR 'brain ischemia'/exp OR 'neonatal encephalopathy' OR 'hypoxic ischemic encephalopathy' OR 'hie' OR 'perinatal asphyxia' OR 'birth asphyxia')
```

### [Block B] Intervention
```
('induced hypothermia'/exp OR 'therapeutic hypothermia' OR 'body temperature management' OR 'cooling' OR 'head cooling' OR 'whole body cooling')
```

### [Block C] Setting
```
('developing country'/exp OR 'low income country'/exp OR 'middle income country'/exp OR 'lmic' OR 'low resource setting' OR 'resource limited setting')
```

### [Combined] Master Embase String
```
('asphyxia neonatorum'/exp OR 'brain ischemia'/exp OR 'neonatal encephalopathy' OR 'hypoxic ischemic encephalopathy') AND ('induced hypothermia'/exp OR 'therapeutic hypothermia' OR 'cooling') AND ('developing country'/exp OR 'low income country'/exp OR 'middle income country'/exp OR 'lmic')
```

---

## 3. Secondary Filters (Optional)

### Post-HELIX Date Filter
To focus specifically on the window after the HELIX trial publication:
- **PubMed:** `AND (2021/01/01:3000/12/31[Date - Publication])`
- **Embase:** `AND [2021-2026]/py`

### Clinical Trial Filter (Cochrane Highly Sensitive Filter)
```
(randomized controlled trial [pt] OR controlled clinical trial [pt] OR randomized [tiab] OR placebo [tiab] OR clinical trials as topic [mesh: noexp] OR randomly [tiab] OR trial [ti]) NOT (animals [mesh] NOT humans [mesh])
```

## Maintenance Note
Last updated: 2026-03-09
Methodology: MeSH-optimized Boolean strings focusing on high sensitivity to capture the high heterogeneity of LMIC reporting.
