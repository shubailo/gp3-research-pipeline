# Metabolism Data: Outliers and Exclusions

## 1. Exclusions based on Metadata Comments

- **NF12_aMSH ID 7208:** VO2 PG-
- **NF12_aMSH ID 7213:** PG- (szétcsúszott)
- **NF12_aMSH ID 7215:** PG- (szétcsúszott)
- **NF12_aMSH ID 7213:** ÜL
- **NF12_aMSH ID 7214:** Tc magas nem kap PG-t
- **NF12_aMSH ID 7270:** PG-(lyukas)
- **TR12_aMSH ID 7678:** magas Tc,nem kap PG-t
- **TR12_Leptin ID 7675:** beszaladt a PG is +
- **TR12_Leptin ID 7678:** magas Tc,nem kap PG-t
- **TR12_aMSH ID 7318:** PGneg.
- **TR12_aMSH ID 7323:** PGpoz.
- **TR12_aMSH ID 7328:** PGpoz.
- **TR12_aMSH ID 7329:** PGpoz.
- **TR12_aMSH ID 7375:** szétcsúszott
- **TR12_aMSH ID 7380:** szétcsúszott
- **TR12_Leptin ID 7245:** PG+(05.10.) Fürdetés reggel Lyukas kanül
- **TR12_Leptin ID 7246:** PG+(05.10.) Fürdetés reggel
- **TR12_Leptin ID 7247:** PG+(05.10.) Fürdetés reggel szétcsúszott kanül
- **TR12_Leptin ID 7359:** ÜL
- **TR12_Leptin ID 7363:** lyukas kanül
- **TR12_Leptin ID 7364:** lyukas kanül
- **CR12_aMSH ID 7338:** szétrágta a kanült
- **CR12_aMSH ID 7339:** szétrágta a kanült
- **CR12_aMSH ID 7340:** szétcsúszott
- **CR12_aMSH ID 7344:** lyukas a kanül
- **CR12_aMSH ID 7345:** lyukas a kanül
- **CR12_Leptin ID 7336:** (PG-)
- **CR12_Leptin ID 7337:** (PG-)
- **CR12_Leptin ID 7338:** (PG+)
- **CR12_Leptin ID 7339:** (PG+)
- **CR12_Leptin ID 7340:** (PG nincs)
- **CR12_Leptin ID 7341:** (PG+)
- **CR12_Leptin ID 7346:** (PG+)
- **CR12_Leptin ID 7347:** (PG+)
- **CR12_Leptin ID 7338:** nehezen megy be
- **CR12_Leptin ID 7344:** szétcsúszott
- **CR12_Leptin ID 7341:** nehezen megy be
- **CR12_Leptin ID 7438:** PG- gennyes a feje
- **CR12_Leptin ID 7441:** lyukas a kanül
- **CR12_Leptin ID 7432:** szétcsúszott
- **CR12_aMSH ID 7200:** magas Tc nem kap PG-t
- **CR12_Leptin ID 7201:** PG+(0123)
- **CR12_Leptin ID 7202:** PG+(0123)
- **CR12_Leptin ID 7204:** PG-(0124)
- **CR12_Leptin ID 7205:** PG-(0124)
- **CR12_Leptin ID 7207:** PG+(0124)

## 2. Statistical Outliers

### TR12_Control
- **dVCO2:** IDs [7243] (Values: [np.float64(1.338)])

### TR12_aMSH
- No obvious statistical outliers based on mean over time.

### TR12_Leptin
- **dVCO2:** IDs [7675, 7245, 7361] (Values: [np.float64(-4.584), np.float64(-2.586), np.float64(1.093)])
- **dVO2:** IDs [7675, 7245, 7361] (Values: [np.float64(-5.372), np.float64(-2.708), np.float64(1.476)])

### NF12_Control
- **VO2:** IDs ['6548.1', '6545.2'] (Values: [np.float64(8.967), np.float64(7.226)])
- **dVO2:** IDs ['6547.1', '6548.1'] (Values: [np.float64(-5.393), np.float64(-5.148)])

### NF12_aMSH
- **VO2:** IDs ['7208.1'] (Values: [np.float64(9.877)])
- **dVO2:** IDs ['7216.1'] (Values: [np.float64(-3.245)])

### NF12_Leptin
- **EE:** IDs ['7240.1'] (Values: [np.float64(95.384)])
- **RQ:** IDs [7246, 7247] (Values: [np.float64(0.713), np.float64(0.68)])
- **dVCO2:** IDs [7243] (Values: [np.float64(1.338)])

### CR12_Control
- No obvious statistical outliers based on mean over time.

### CR12_aMSH
- No obvious statistical outliers based on mean over time.

### CR12_Leptin
- **dVCO2:** IDs [7346] (Values: [np.float64(-4.136)])
- **dVO2:** IDs [7347] (Values: [np.float64(-4.514)])

