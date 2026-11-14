#!/usr/bin/env python3
"""
ai_screener.py — GP3 Hybrid NLP Screener (Tier 1: TF-IDF Relevance Engine)
========================================================================
Szisztematikus irodalmi szűrés (Title & Abstract Screening) segédeszköz.
A manuálisan / kanonikusan beválogatott (INCLUDE) tanulmányok szövegeiből
(cím + absztrakt) TF-IDF reprezentációt és centroidot képez, majd rangsorolja
az összes EXCLUDE (vagy szűrendő) rekordot koszinusz-hasonlóság alapján.

Ez lehetővé teszi, hogy a határeseteket (boundary cases) a kutató / LLM
tételesen, de célzottan tekintse át (Tier 2 review), kizárva a téves kizárásokat
(false negative bias megelőzése).

Használat:
    # 1. Automatikus feloldás a projekt mappájából:
    python src/ai_screener.py --project meta_hyperglycaemia --threshold 0.15

    # 2. Egyedi CSV közvetlen megadásával:
    python src/ai_screener.py --input projects/meta_hyperglycaemia/data/CTM_Screening_Decisions_2981.csv --threshold 0.10

    # 3. Régi kompatibilis hívás:
    python src/ai_screener.py 0.10

Függőségek: scikit-learn, pandas, numpy
"""

import os
import sys
import argparse
from typing import Optional, List, Tuple
import pandas as pd
import numpy as np

# Windows UTF-8 kódolás beállítása
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    print("[ERROR] A scikit-learn csomag nem található! Telepítés: pip install scikit-learn", file=sys.stderr)
    sys.exit(1)


def find_project_csv(project_slug: str) -> Optional[str]:
    """Megkeresi a projekt screening döntési CSV fájlját a kanonikus könyvtárakban."""
    candidates = [
        os.path.join(PROJECT_ROOT, "projects", project_slug, "data", "CTM_Screening_Decisions_2981.csv"),
        os.path.join(PROJECT_ROOT, "projects", project_slug, "data", f"screening_decisions_{project_slug}.csv"),
        os.path.join(PROJECT_ROOT, "projects", project_slug, "data", "screening_decisions.csv"),
    ]
    data_dir = os.path.join(PROJECT_ROOT, "projects", project_slug, "data")
    if os.path.exists(data_dir):
        for f in os.listdir(data_dir):
            if f.endswith(".csv") and ("screening" in f.lower() or "decisions" in f.lower()):
                cand = os.path.join(data_dir, f)
                if cand not in candidates:
                    candidates.append(cand)

    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def run_screener(csv_path: str, threshold: float = 0.10, out_dir: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Végrehajtja a Tier 1 TF-IDF rangsorolást a megadott CSV fájlon.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"A megadott CSV nem található: {csv_path}")

    if out_dir is None:
        out_dir = os.path.join(PROJECT_ROOT, "scratch")
    os.makedirs(out_dir, exist_ok=True)

    out_all_path = os.path.join(out_dir, "ranked_exclude_candidates.csv")
    out_queue_path = os.path.join(out_dir, "tier2_review_queue.csv")

    print("=" * 70)
    print("  GP3 MEDICAL RESEARCH PIPELINE | HYBRID NLP SCREENER (TIER 1)")
    print(f"  Bemeneti CSV:   {csv_path}")
    print(f"  Küszöbérték:    {threshold:.2f}")
    print(f"  Kimeneti mappa: {out_dir}")
    print("=" * 70)

    # 1. Betöltés
    print("\n[1/5] Adatbázis betöltése...")
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    print(f"      Sorok száma: {len(df)}")

    # Oszlop-azonosítás rugalmasan
    cols = df.columns.tolist()
    decision_col = next((c for c in cols if "gomb" in c.lower() or "döntés" in c.lower() or "decision" in c.lower()), None)
    title_col = next((c for c in cols if "cím" in c.lower() or "title" in c.lower()), None)
    abstract_col = next((c for c in cols if "absztrakt" in c.lower() or "abstract" in c.lower()), None)

    if not decision_col or not title_col or not abstract_col:
        raise ValueError(f"Nem sikerült azonosítani a kötelező oszlopokat! Talált oszlopok: {cols}")

    print(f"      Azonosított oszlopok: Döntés='{decision_col}', Cím='{title_col}', Absztrakt='{abstract_col}'")
    decision_counts = df[decision_col].value_counts().to_dict()
    print(f"      Döntések megoszlása: {decision_counts}")

    # 2. Szövegek előkészítése
    df["_text"] = (df[title_col].fillna("").astype(str) + " " + df[abstract_col].fillna("").astype(str)).str.strip()

    include_mask = df[decision_col].str.contains("include|zöld pipa", case=False, na=False)
    exclude_mask = df[decision_col].str.contains("exclude|piros x", case=False, na=False)

    include_df = df[include_mask].copy()
    exclude_df = df[exclude_mask].copy()

    if len(include_df) == 0:
        raise ValueError("Nem található INCLUDE rekord az adatbázisban, nem lehet referenciamodellt tanítani!")

    print(f"\n[2/5] Korpusz megoszlás:")
    print(f"      INCLUDE (referencia profil): {len(include_df)} rekord")
    print(f"      EXCLUDE (rangsorolandó):     {len(exclude_df)} rekord")

    # 3. TF-IDF modellépítés
    print("\n[3/5] TF-IDF vektorizáció és centroid képzés...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        max_features=15000,
        stop_words=None,
    )

    all_texts = df["_text"].tolist()
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    include_indices = include_df.index.tolist()
    include_vectors = tfidf_matrix[include_indices]
    include_centroid = np.asarray(include_vectors.mean(axis=0))

    feature_names = vectorizer.get_feature_names_out()
    centroid_flat = include_centroid.flatten()
    top20_idx = centroid_flat.argsort()[::-1][:15]
    print("      Top 15 legfontosabb referencia-kifejezés (TF-IDF súly):")
    for i in top20_idx:
        print(f"        • {centroid_flat[i]:.4f}  {feature_names[i]}")

    # 4. Koszinusz hasonlóság
    print(f"\n[4/5] Hasonlóság kalkuláció {len(exclude_df)} kizárt rekordon...")
    exclude_indices = exclude_df.index.tolist()
    exclude_vectors = tfidf_matrix[exclude_indices]
    scores = cosine_similarity(exclude_vectors, include_centroid.reshape(1, -1)).flatten()

    exclude_df["TF_IDF_Score"] = scores
    exclude_df_sorted = exclude_df.sort_values("TF_IDF_Score", ascending=False).reset_index(drop=True)
    exclude_df_sorted.insert(0, "Rank", range(1, len(exclude_df_sorted) + 1))

    print(f"      Statisztika: Max={scores.max():.4f}, Mean={scores.mean():.4f}, Median={np.median(scores):.4f}")
    print(f"      Rekordok száma küszöbérték szerint:")
    for th in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
        print(f"        > {th:.2f}: {(scores > th).sum():4d} rekord")

    # 5. Mentés
    print(f"\n[5/5] Eredmények mentése...")
    save_cols = [c for c in ["Rank", "TF_IDF_Score", "Rayyan ID (Sorszám)", "Első Szerző & Év", title_col, "Folyóirat", decision_col, "Rayyan Kizárási Ok (Reason)", "Rövid Orvosi Indoklás (HU)", abstract_col] if c in exclude_df_sorted.columns]
    
    exclude_df_sorted[save_cols].to_csv(out_all_path, index=False, encoding="utf-8-sig")
    print(f"      ✅ Teljes rangsor mentve: {out_all_path}")

    tier2_df = exclude_df_sorted[exclude_df_sorted["TF_IDF_Score"] >= threshold].copy()
    tier2_df[save_cols].to_csv(out_queue_path, index=False, encoding="utf-8-sig")
    print(f"      ✅ Tier 2 Queue mentve:   {out_queue_path} ({len(tier2_df)} rekord >= {threshold:.2f})")

    # Top 5 előnézet
    print("\n" + "-" * 70)
    print("  TOP 5 HATÁRESET (Tier 2 prioritás):")
    print("-" * 70)
    for _, row in tier2_df.head(5).iterrows():
        t = str(row.get(title_col, ""))[:55]
        s = row.get("Első Szerző & Év", "N/A")
        print(f"  Rank {int(row['Rank']):>2} | Score: {row['TF_IDF_Score']:.4f} | {s} | {t}...")

    print("=" * 70)
    return exclude_df_sorted, tier2_df


def main():
    parser = argparse.ArgumentParser(description="GP3 Hybrid NLP Screener — Tier 1 TF-IDF Relevance Engine")
    parser.add_argument("--project", type=str, default="meta_hyperglycaemia", help="Projekt azonosító (pl. meta_hyperglycaemia)")
    parser.add_argument("--input", type=str, default=None, help="Közvetlen elérési út a screening CSV fájlhoz")
    parser.add_argument("--threshold", type=float, default=0.10, help="Tier 2 review küszöbérték (alapértelmezett: 0.10)")
    parser.add_argument("--output-dir", type=str, default=None, help="Kimeneti könyvtár (alapértelmezett: scratch/)")

    if len(sys.argv) == 2 and not sys.argv[1].startswith("-"):
        try:
            th = float(sys.argv[1])
            args = parser.parse_args([])
            args.threshold = th
        except ValueError:
            args = parser.parse_args()
    else:
        args = parser.parse_args()

    csv_path = args.input
    if not csv_path:
        csv_path = find_project_csv(args.project)
        if not csv_path:
            default_path = os.path.join(PROJECT_ROOT, "projects", "meta_hyperglycaemia", "data", "CTM_Screening_Decisions_2981.csv")
            if os.path.exists(default_path):
                csv_path = default_path
            else:
                print(f"[ERROR] Nem található screening CSV a '{args.project}' projekthez!", file=sys.stderr)
                sys.exit(1)

    try:
        run_screener(csv_path=csv_path, threshold=args.threshold, out_dir=args.output_dir)
    except Exception as e:
        print(f"[ERROR] Hiba a szűrés futtatása során: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
