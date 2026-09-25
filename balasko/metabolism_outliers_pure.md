# Metabolikus outlierek – Tisztán adat-alapú elemzés

> Z-score küszöb: **2.0** | IQR szorzó: **1.5x** | Post-injekciós adatok (t ≥ 0 min)

Vizsgált paraméterek: VO2, VCO2, RQ, EE, dVO2, dVCO2

## 🔴 ERŐS outlierek (z > 2.0 ÉS IQR)

| Csoport | ID | Paraméter | Állat átlaga | Csoport átlaga | SD | z-score | Irány |
|---------|-----|-----------|-------------|----------------|-----|---------|-------|
| CR12_Leptin | **7346** | dVCO2 | -4.268 | -0.764 | 1.042 | -3.36 | ALACSONY |
| CR12_Leptin | **7347** | dVO2 | -4.611 | -0.450 | 1.124 | -3.70 | ALACSONY |
| NF12_Control | **6545.2** | VO2 | 7.420 | 12.266 | 1.710 | -2.83 | ALACSONY |
| NF12_Control | **6546.3** | RQ | 1.029 | 0.910 | 0.044 | +2.74 | MAGAS |
| NF12_Control | **6547.1** | dVO2 | -6.689 | -0.435 | 2.349 | -2.66 | ALACSONY |
| NF12_Control | **6548.1** | VO2 | 8.502 | 12.266 | 1.710 | -2.20 | ALACSONY |
| NF12_Control | **6548.1** | dVO2 | -5.613 | -0.435 | 2.349 | -2.20 | ALACSONY |
| NF12_Leptin | **7247** | RQ | 0.677 | 0.826 | 0.057 | -2.60 | ALACSONY |
| NF12_aMSH | **7208.1** | VO2 | 9.772 | 16.205 | 2.288 | -2.81 | ALACSONY |
| TR12_Control | **7243** | dVCO2 | 1.298 | -0.394 | 0.779 | +2.17 | MAGAS |
| TR12_Leptin | **7675** | dVCO2 | -4.921 | -0.969 | 1.445 | -2.73 | ALACSONY |
| TR12_Leptin | **7675** | dVO2 | -5.741 | -0.808 | 1.720 | -2.87 | ALACSONY |

## 🟡 Gyenge outlierek (z > 2.0 VAGY IQR)

| Csoport | ID | Paraméter | Állat átlaga | Csoport átlaga | SD | z-score | Irány |
|---------|-----|-----------|-------------|----------------|-----|---------|-------|
| CR12_Leptin | **7430** | dVO2 | 1.802 | -0.450 | 1.124 | +2.00 | MAGAS |
| NF12_Leptin | **7240.1** | EE | 96.035 | 115.716 | 8.627 | -2.28 | ALACSONY |
| NF12_Leptin | **7240.1** | VO2 | 13.759 | 16.639 | 1.333 | -2.16 | ALACSONY |
| NF12_Leptin | **7243** | dVCO2 | 1.298 | -0.312 | 0.764 | +2.11 | MAGAS |
| NF12_Leptin | **7246** | RQ | 0.709 | 0.826 | 0.057 | -2.04 | ALACSONY |
| NF12_aMSH | **7208.1** | RQ | 1.117 | 0.942 | 0.063 | +2.78 | MAGAS |
| NF12_aMSH | **7216.1** | dVO2 | -3.081 | -0.549 | 1.080 | -2.34 | ALACSONY |
| TR12_Control | **7240.1** | EE | 96.035 | 114.472 | 8.688 | -2.12 | ALACSONY |
| TR12_Control | **7247** | RQ | 0.677 | 0.817 | 0.061 | -2.29 | ALACSONY |
| TR12_Leptin | **7245** | dVCO2 | -2.814 | -0.969 | 1.445 | -1.28 | ALACSONY |
| TR12_Leptin | **7245** | dVO2 | -2.918 | -0.808 | 1.720 | -1.23 | ALACSONY |
| TR12_Leptin | **7246** | VO2 | 18.744 | 15.133 | 1.657 | +2.18 | MAGAS |
| TR12_Leptin | **7361** | dVCO2 | 1.011 | -0.969 | 1.445 | +1.37 | MAGAS |
| TR12_Leptin | **7361** | dVO2 | 1.550 | -0.808 | 1.720 | +1.37 | MAGAS |
| TR12_aMSH | **7318** | dVCO2 | 1.906 | -1.899 | 1.869 | +2.04 | MAGAS |
| TR12_aMSH | **7318** | dVO2 | 2.711 | -1.691 | 1.911 | +2.30 | MAGAS |
| TR12_aMSH | **7328** | dVO2 | -5.678 | -1.691 | 1.911 | -2.09 | ALACSONY |
| TR12_aMSH | **7375** | EE | 85.905 | 122.728 | 16.949 | -2.17 | ALACSONY |
| TR12_aMSH | **7375** | VO2 | 11.670 | 17.536 | 2.686 | -2.18 | ALACSONY |

