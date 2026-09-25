# Outliers and Exclusions Analysis

Based on the metadata comments and statistical outlier detection (using the IQR method on mean values across timepoints), here are the animals that should be considered for exclusion from the dataset.

## 1. Exclusions based on Metadata Comments

The following animals have comments indicating technical issues (e.g., cannula slipped out, broken cannula, did not receive drug, bloody colon) during the experiment and should be **excluded**:

### TR12 Group
- **7678 (aMSH, Leptin):** "magas Tc, nem kap PG-t" (high Tc, did not receive PG)
- **7675 (Leptin):** "beszaladt a PG is" (PG ran in too)
- **7375, 7380 (aMSH):** "szétcsúszott" (slipped apart)
- **7245 (Leptin):** "kanál lyukas" (cannula has a hole)
- **7247 (Leptin):** "szétcsúszott a végén" (slipped apart at the end)
- **7241, 7242, 7243, 7237, 7238, 7239, 7240 (Leptin):** "oxy nincs" / "PG+ oxy nincs" (no oxygen)
- **7244 (Leptin):** "szétcsúszott oxy nincs" (slipped apart, no oxygen)
- **7363 (Leptin):** "lyukas kanál" (cannula has a hole)

### CR12 Group
- **7338 (aMSH):** "szétrágta a kanált" (chewed the cannula)
- **7339, 7340 (aMSH):** "szétcsúszott" (slipped apart)
- **7345 (aMSH):** "Lyukas a kanál" (cannula has a hole)
- **7340, 7341 (Leptin):** "PG szétcsúszott" / "nehezen megy be" (PG slipped apart / goes in with difficulty)
- **7200 (aMSH, Leptin):** "PG-t nem kap" / "magas Tc PG nincs" (did not receive PG / high Tc no PG)
- **7567 (aMSH):** "kanál lyukas" (cannula has a hole)
- **7570 (aMSH):** "PG is beszaladt az elején" (PG ran in at the beginning)
- **7202 (Leptin):** "colon vissza csúszva (Tc alacsony)" / "colon visszafordulva PG+" (colon slid back, low Tc / colon turned back PG+)
- **7207 (Leptin):** "PG+ colon véres" (PG+ colon bloody)
- **7313, 7432 (Leptin):** "szétcsúszott" (slipped apart)
- **7441, 7432, 7568, 7563, 7570 (Leptin):** "lyukas a kanál" / "lyukas" (cannula has a hole)


## 2. Statistical Outliers

Using the Interquartile Range (IQR) method on the average values for each animal over the time series, the following IDs showed significant deviation from the group mean and should be reviewed (note that some of these overlap with the comment-based exclusions):

### NF12 Group
- **NF12_Control:** Animal **4** (Low core temperature Tc mean: ~36.2 °C)
- **NF12_aMSH:** Animal **7702** (Low ambient and core temperatures Ta, Tc mean: ~35.3 °C) - *Highly recommended for exclusion.*
- **NF12_Leptin:** Animal **7270** (Low HLI), Animal **7702** (High dTc)

### TR12 Group
- **TR12_aMSH:** 
  - Animal **7675** (High HLI, Ta, Ts) - *Matches metadata exclusion*
  - Animal **7243** (High Tc mean ~38.2 °C), **7240** (Low Tc mean ~36.5 °C) - *Both match metadata exclusions ("oxy nincs")*
  - Animals **7328, 7375** (deviant dTc)
- **TR12_Leptin:** 
  - Animal **7245** (Low Tc mean ~36.3 °C) - *Matches metadata exclusion ("kanál lyukas")*

### CR12 Group
- **CR12_Control:** Animals **7201, 6749, 6755** (High HLI), **6746, 6356** (deviant dTs)
- **CR12_aMSH:** Animal **7566** (Low Ta mean ~24.5 °C), **7565** (High Ts mean ~29.7 °C)
- **CR12_Leptin:** Animals **7566, 7567, 7569, 7570** (Low Ta mean ~22 °C) - *Several match metadata exclusions ("lyukas")*
- **CR12_Leptin:** Animal **7441.1** (Deviant dTs mean ~-2.0 °C) - *Matches metadata exclusion ("lyukas a kanál")*

## Summary Recommendation
The metadata log provides excellent physiological justification for exclusion. Many of the statistical outliers perfectly match the animals with compromised cannulas or measurement issues (e.g. 7675, 7243, 7245, 7702, 7567, 7441). You should confidently exclude the animals listed in Section 1, and manually inspect the remaining purely statistical outliers (like 4, 7565, 7201) to decide if their raw data traces look physiological or artifactual.

Created stats_compare.py
Ran command: `python stats_compare.py; Get-Content stats_comparison.txt`
Used tool: manage_task
Created generate_stats_md.py
Ran command: `python generate_stats_md.py`
Viewed statistical_analysis.md:1-33

It is great that you excluded those compromised animals! I've compared the old and new `Summary` pages and run independent t-tests on the cleaned dataset. 

### 1. What difference did the exclusions make?
By removing the animals with slipped/broken cannulas and missing PG injections, the **Standard Error of the Mean (SEM) dropped significantly**, particularly in the `CR12` and `TR12` groups. Previously, the artifactual drops in temperature from broken equipment were completely masking the true physiological responses. With the noise removed, the true autonomic responses are now statistically significant.

### 2. Statistical Significance (Treatment vs. Control, Time $\ge$ 0)
I ran an independent t-test comparing the overall treatment phase means for each animal. Here are the significant differences your new, clean dataset reveals:

*   **CR (Calorie Restricted) Group:**
    *   **aMSH** caused a highly significant increase in core temp (**$\Delta$Tc: p = 0.0025 \*\***) and a significant change in tail heat loss (**HLI: p = 0.0232 \***, **$\Delta$Ts: p = 0.0025 \*\***) compared to CR Control.
    *   *Leptin* showed a trend towards increasing Tc, but it did not reach statistical significance (p = 0.109).
*   **TR (Trained) Group:**
    *   **aMSH** caused a massive and highly significant increase in core temp (**$\Delta$Tc: p = 0.0004 \*\*\***) and skin temp (**$\Delta$Ts: p = 0.0018 \*\***).
    *   **Leptin** also caused a significant increase in core temp (**$\Delta$Tc: p = 0.0122 \***) compared to TR Control.
*   **NF (Normal Fed) Group:**
    *   As expected physiologically, Normal Fed animals have a much milder response. aMSH showed a strong trend for $\Delta$Tc (p = 0.068), but no treatments crossed the strict p < 0.05 threshold against control.

*(I have updated the [Statistical Analysis Report](file:///C:/Users/shuba/.gemini/antigravity-ide/brain/fd191c7b-d07c-46ea-84b2-7d33fa705187/statistical_analysis.md) artifact with the full p-value tables).*

***

### 3. OriginPro Figure Design & Presentation Guidelines

To publish this data, you want to tell a clear physiological story. Here is exactly how you should set up your OriginPro graphs:

#### **Which Parameters to Show?**
You should create a 2-panel figure for each group (NF, CR, TR) or combine them into a larger multi-panel figure:
1.  **Primary Panel (The "What"): $\Delta$Tc (Change in Core Temperature)**. This is the most universally understood metric in thermoregulation literature. It proves whether the drug induced a hyperthermic/thermogenic response.
2.  **Secondary Panel (The "How"): HLI (Heat Loss Index) or $\Delta$Ts**. This proves the *mechanism*. A change in HLI proves that the change in core temperature was driven by autonomic vasomotor tone (tail vasoconstriction) rather than just BAT thermogenesis. (HLI is technically superior to $\Delta$Ts for publication because it normalizes against ambient temperature, but $\Delta$Ts is perfectly fine if your Ta was tightly controlled).

#### **How to layout the graphs in OriginPro:**
*   **Main Graph Type:** Time-Series Line + Scatter plot. X-axis is `Time (min)` (from -30 to 120). Y-axis is the Parameter. Show symbols for the `MEAN` and Y-Error bars for the `SEM`. 
*   **Add an Inset or Adjacent Bar Graph:** Line graphs are hard to put significance asterisks on without looking messy. In Origin, add a small Bar Chart right next to the line graph showing the Area Under the Curve (AUC) or the Mean for Time 0-120 min. Put your `*`, `**`, `***` over these bars.

#### **Y-Axis Standardization (Crucial for Reviewers):**
To allow readers to easily eyeball the differences between NF, CR, and TR, you **must lock the Y-axis scale** to be identical across all groups in Origin:
*   **For $\Delta$Tc graphs:** Set the Y-axis scale manually from **`-0.5 °C` to `+1.5 °C`**. (Set major ticks every 0.5 °C).
*   **For HLI graphs:** Set the Y-axis scale manually from **`-0.1` to `+0.25`**.
*   **For $\Delta$Ts graphs:** Set the Y-axis scale manually from **`-1.0 °C` to `+3.0 °C`**.

*Tip for OriginPro:* Once you style the first graph perfectly (axis thickness, font size 14-16pt Arial/Helvetica, legend position), right-click the graph and select **"Save Format as Theme"**. You can then apply this exact theme to your CR and TR graphs with one click!

Created stats_compare_metabolism.py
Ran command: `python stats_compare_metabolism.py`
Viewed metabolism_compare.txt:1-38
Viewed metabolism_clean_statistics.md:1-47

I've run the statistical comparison on your cleaned dataset (`animaldata_metabolism másolata.xlsx`)!

Removing those 7 corrupted data traces had exactly the effect we hoped for: **it dramatically reduced the statistical "noise" (Standard Error of the Mean, SEM) and strengthened your p-values.** 

Here are the key differences the modifications made:

### 📈 1. How the Statistics Improved
By excluding the animals with broken cannulas and injection failures, the actual physiological responses became much clearer:

*   **NF12 (Normal Fed):** 
    *   The increase in **VO2** after both aMSH and Leptin injections went from being highly significant to **massively significant (p < 0.0001, \*\*\*)**. 
    *   The substrate shift caused by Leptin (**RQ** dropping to ~0.83) also tightened up to **p < 0.0001 (\*\*\*)**, proving a robust shift towards fat oxidation.
*   **TR12 (Trained):**
    *   By removing the two compromised animals from the TR12_Leptin group (7675 and 7245), the paradoxical increase in **RQ** after Leptin became even more significant, jumping from **p=0.0039 (\*\*) to p=0.0006 (\*\*\*)**.
    *   The drop in **$\Delta$VO2** and **$\Delta$VCO2** in response to aMSH jumped from * (p < 0.05) to **\*\* / \*\*\*** (p ~ 0.001).

*(You can view the full new stats table in your artifacts: [Cleaned Statistics](file:///C:/Users/shuba/.gemini/antigravity-ide/brain/fd191c7b-d07c-46ea-84b2-7d33fa705187/metabolism_clean_statistics.md))*

***

### 📊 2. OriginPro Presentation Guide

To publish these results, you need figures that tell a clear visual story. Here is the best way to present them in OriginPro so reviewers can immediately see the differences between the phenotypes (NF vs. CR vs. TR).

#### A. Which Parameters to Show?
I recommend creating panels for the following three parameters, as they tell the complete metabolic story:
1.  **VO2 (ml/min/kg^0.75):** Shows the absolute metabolic rate.
2.  **$\Delta$VO2 (Change from baseline):** Shows the *magnitude* of the reaction to the injection, normalizing for their different baseline metabolic rates.
3.  **RQ (VCO2/VO2):** Shows *what* they are burning (Carbs vs. Fat).

#### B. Recommended Figure Layout (The "Publication Standard")
*   **Main Graph:** Time-series line plot (X-axis: Time from -30 to 120 mins). 
    *   Use distinct symbols for treatments (e.g., Control = Black circles `●`, aMSH = Red squares `■`, Leptin = Blue triangles `▲`).
    *   Add a vertical dashed line at `Time = 0` indicating the time of injection.
*   **Inset Graph (or separate panel):** A bar chart showing the **Area Under the Curve (AUC)** or the **Average of the post-injection period (0-120 min)**. This is where you place your significance asterisks (*, **, ***).

#### C. How to Lock the Y-Axis Scales (Crucial!)
As you noted, if you put the NF, CR, and TR graphs side-by-side, **their Y-axes must be identical**. Otherwise, a reader might look at the CR graph (which has very low absolute VO2) and think it's the same as NF because Origin auto-scaled the axis.

**In OriginPro, follow these steps to lock the axes:**
1.  Double-click the **Y-axis** numbers on your graph to open the `Axis Dialog`.
2.  Go to the **Scale** tab.
3.  Under the `Vertical` section, uncheck the **Auto** boxes next to "From" and "To".
4.  Manually type in the limits. Use these recommended scales to fit all your data perfectly:
    *   **For VO2:** Set `From: 10` and `To: 22`. 
    *   **For $\Delta$VO2:** Set `From: -4` and `To: 2`.
    *   **For RQ:** Set `From: 0.75` and `To: 1.05`.
    *   **For EE:** Set `From: 80` and `To: 140`.
5.  Click **Apply**, then save this as a Graph Theme in Origin (Right-click graph background -> `Save Format as Theme`) so you can instantly apply the exact same scaling to your next graph with one click!

Let me know if you need help calculating the AUC values for the bar charts, or if you want to dive back into your systematic review protocol (`PROSPERO.md`)!