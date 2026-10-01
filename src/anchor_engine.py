#!/usr/bin/env python3
"""
anchor_engine.py
================
GP3 Anchor Engine (Pillar 1 & Pillar 2 Implementation)
Strictly enforces:
  - Pillar 1: Hierarchical 2D Matrix Anchor & Column Channel Projection
  - Pillar 2: Mathematical Checksum Invariance (n/N == reported_pct)
      * Derived precision tolerance: tol = 0.5 * 10^(-d) + 1e-9
      * Discriminative power verification & tolerance window [n_min, n_max]
  - Fail-Loud Error Policies (never continue silently on ambiguity or empty clips)
  - Tamper-Evidence Context Hashing (SHA-256)
  - Cochrane Chapter 5 Human Confirmation Gate (PENDING -> CONFIRMED)
  - Visual verification crop generation for auditable human double-check

Standard: Cochrane Handbook v6.5 (Chapter 5) · CTM Template v9
Version: 1.2 (Precision-Calibrated Anchor Engine)
"""

import os
import re
import math
import hashlib
import datetime
import fitz  # PyMuPDF


# ==============================================================================
# 1. Custom Exceptions (Fail-Loud Policy)
# ==============================================================================

class AnchorEngineError(Exception):
    """Base class for all Anchor Engine errors."""
    pass


class EmptyCellError(AnchorEngineError):
    """Raised when the target intersection clip contains no text."""
    pass


class AmbiguousCellError(AnchorEngineError):
    """Raised when multiple conflicting numbers or unresolved structures exist."""
    pass


class AmbiguousRowError(AmbiguousCellError):
    """Raised when multiple identical row labels appear on the page without parent_context."""
    pass


class RowNotFoundError(AnchorEngineError):
    """Raised when the specified row header cannot be located on the target page."""
    pass


class ColumnChannelNotFoundError(AnchorEngineError):
    """Raised when the specified column header cannot be located on the header page."""
    pass


class MathChecksumError(AnchorEngineError):
    """Raised when reported percent deviates from n / N by more than precision tolerance."""
    pass


class OutOfChannelError(AnchorEngineError):
    """Raised when the cell text falls outside the projected column channel."""
    pass


class HumanConfirmationPendingError(AnchorEngineError):
    """Raised when unconfirmed PENDING clinical data is promoted to synthesis Excel."""
    pass


# ==============================================================================
# 2. Data Classes / Structures
# ==============================================================================

class ColumnChannel:
    def __init__(self, name, header_page, x0, x1, header_rect):
        self.name = name
        self.header_page = header_page  # 1-indexed
        self.x0 = float(x0)
        self.x1 = float(x1)
        self.header_rect = header_rect

    def __repr__(self):
        return f"ColumnChannel('{self.name}', page={self.header_page}, x=[{self.x0:.1f}, {self.x1:.1f}])"


class RowBand:
    def __init__(self, name, target_page, y0, y1, row_rect, full_line_text=""):
        self.name = name
        self.target_page = target_page  # 1-indexed
        self.y0 = float(y0)
        self.y1 = float(y1)
        self.row_rect = row_rect
        self.full_line_text = full_line_text

    def __repr__(self):
        return f"RowBand('{self.name}', page={self.target_page}, y=[{self.y0:.1f}, {self.y1:.1f}])"


# ==============================================================================
# 3. Pillar 1: Hierarchical 2D Matrix Anchor & Channel Projection
# ==============================================================================

def detect_column_channel(doc, header_page_num, col_query, subcol_query=None, x_padding=25.0):
    """
    Detects the horizontal bounds [x0, x1] of a column header on header_page_num.
    Supports hierarchical sub-columns (e.g., 'Median (IQR) or N (%)' within 'Hypoglycemia').
    header_page_num is 1-indexed.
    """
    p_idx = header_page_num - 1
    if p_idx < 0 or p_idx >= len(doc):
        raise ColumnChannelNotFoundError(f"Page {header_page_num} out of bounds in PDF (len={len(doc)})")

    page = doc[p_idx]
    rects = page.search_for(col_query)

    # Fallback to first words if exact string with line breaks
    if not rects and " " in col_query:
        words = col_query.split()
        rects = page.search_for(" ".join(words[:2]))

    if not rects:
        raise ColumnChannelNotFoundError(
            f"Column header '{col_query}' not found on header page {header_page_num}"
        )

    # Pick the match highest on page (smallest y0) in table header zone
    header_rect = sorted(rects, key=lambda r: r.y0)[0]

    # If a subcolumn is requested, find it under/within the main header span
    if subcol_query:
        sub_rects = page.search_for(subcol_query)
        valid_sub = [
            r for r in sub_rects
            if r.y0 >= header_rect.y0 - 5.0 and (header_rect.x0 - 30.0 <= r.x0 <= header_rect.x1 + 30.0)
        ]
        if valid_sub:
            header_rect = sorted(valid_sub, key=lambda r: r.y0)[0]

    # Expand by x_padding to cover column content width
    x0 = max(0.0, header_rect.x0 - x_padding)
    x1 = min(page.rect.width, header_rect.x1 + x_padding)

    return ColumnChannel(
        name=col_query if not subcol_query else f"{col_query} -> {subcol_query}",
        header_page=header_page_num,
        x0=x0,
        x1=x1,
        header_rect=header_rect
    )


def _get_row_label_text(page, rect, max_x=220.0):
    """
    Extracts the textual label of a table row stub starting around rect.
    Preserves all words within the matched rect (e.g. '18 months' or '= 2'),
    and stops at subsequent data columns or numbers beyond the stub.
    """
    y_mid = (rect.y0 + rect.y1) / 2.0
    line_words = [
        w for w in page.get_text("words")
        if abs((w[1] + w[3]) / 2.0 - y_mid) < 3.0 and w[0] < max_x
    ]
    line_words.sort(key=lambda w: w[0])

    label_tokens = []
    for w in line_words:
        token = w[4].strip()
        # Words within or overlapping the matched query rect are always part of the label
        if w[0] < rect.x1 + 2.0:
            label_tokens.append(token)
            continue
        # For words beyond rect: stop if it looks like a numeric data cell
        if re.match(r"^\d", token) and not re.match(r"^\d+(?:st|nd|rd|th)$", token.lower()):
            break
        label_tokens.append(token)
    return " ".join(label_tokens).strip()


def find_row_band(doc, target_page_num, row_query, y_padding=1.0, parent_context=None):
    """
    Locates the vertical band [y0, y1] of a row label on target_page_num.
    Enforces exact stub label matching and excludes narrative body text occurrences.
    Fails loudly with AmbiguousRowError if duplicate identical row labels exist without parent_context.
    target_page_num is 1-indexed.
    """
    p_idx = target_page_num - 1
    if p_idx < 0 or p_idx >= len(doc):
        raise RowNotFoundError(f"Page {target_page_num} out of bounds in PDF (len={len(doc)})")

    page = doc[p_idx]
    rects = page.search_for(row_query)

    if not rects and " " in row_query:
        words = row_query.split()
        rects = page.search_for(" ".join(words[:2]))

    if not rects:
        raise RowNotFoundError(
            f"Row query '{row_query}' not found on target page {target_page_num}"
        )

    # Exclude narrative text: Table stub labels must start near the left margin (x < 220)
    # and not be preceded by regular paragraph prose on the same line.
    candidate_matches = []
    norm_query = re.sub(r"[^\w\s]", "", row_query).strip().lower()

    for r in rects:
        # Check if rect starts near the left margin for table stub
        if r.x0 > 220.0:
            continue  # Narrative right column or middle of paragraph

        # Check words preceding rect on the same line
        preceding_words = [
            w for w in page.get_text("words")
            if abs((w[1] + w[3]) / 2.0 - (r.y0 + r.y1) / 2.0) < 3.0 and w[2] < r.x0 - 2.0
        ]
        # In a table stub, the row label is not preceded by narrative prose
        if len(preceding_words) > 2:
            continue

        label_text = _get_row_label_text(page, r)
        norm_label = re.sub(r"[^\w\s]", "", label_text).strip().lower()

        is_exact = (norm_label == norm_query)
        is_prefix = norm_label.startswith(norm_query)

        candidate_matches.append({
            "rect": r,
            "label_text": label_text,
            "norm_label": norm_label,
            "is_exact": is_exact,
            "is_prefix": is_prefix
        })

    # Disambiguate with parent_context if provided
    if parent_context:
        parent_rects = page.search_for(parent_context)
        valid_parents = [
            r for r in parent_rects
            if r.x0 < 220.0 and len([
                w for w in page.get_text("words")
                if abs((w[1] + w[3]) / 2.0 - (r.y0 + r.y1) / 2.0) < 3.0 and w[2] < r.x0 - 2.0
            ]) <= 2
        ]
        if valid_parents:
            p_rect = sorted(valid_parents, key=lambda r: r.y0)[0]
            candidate_matches = [c for c in candidate_matches if c["rect"].y0 >= p_rect.y0 - 2.0]
        elif parent_rects:
            p_rect = sorted(parent_rects, key=lambda r: r.y0)[0]
            candidate_matches = [c for c in candidate_matches if c["rect"].y0 >= p_rect.y0 - 2.0]

    if not candidate_matches:
        raise RowNotFoundError(
            f"Row query '{row_query}' could not be matched to any table row stub on page {target_page_num}."
        )

    # Exact matches take highest priority
    exact_candidates = [c for c in candidate_matches if c["is_exact"]]
    if len(exact_candidates) == 1:
        chosen = exact_candidates[0]
    elif len(exact_candidates) > 1:
        raise AmbiguousRowError(
            f"Row query '{row_query}' matched {len(exact_candidates)} identical table row labels on page {target_page_num}. "
            "Specify parent_context to disambiguate."
        )
    else:
        # Try prefix matches
        prefix_candidates = [c for c in candidate_matches if c["is_prefix"]]
        if len(prefix_candidates) == 1:
            chosen = prefix_candidates[0]
        elif len(prefix_candidates) > 1:
            raise AmbiguousRowError(
                f"Row query '{row_query}' matched multiple ambiguous row stubs: {[c['label_text'] for c in prefix_candidates]}. "
                "Specify parent_context to disambiguate."
            )
        else:
            raise RowNotFoundError(
                f"Row query '{row_query}' does not match stub labels on page {target_page_num}: "
                f"{[c['label_text'] for c in candidate_matches]}"
            )

    row_rect = chosen["rect"]
    line_rect = fitz.Rect(0, max(0.0, row_rect.y0 - y_padding), page.rect.width, min(page.rect.height, row_rect.y1 + y_padding))
    full_line = page.get_text("text", clip=line_rect).strip().replace("\n", " | ")

    return RowBand(
        name=row_query,
        target_page=target_page_num,
        y0=max(0.0, row_rect.y0 - y_padding),
        y1=min(page.rect.height, row_rect.y1 + y_padding),
        row_rect=row_rect,
        full_line_text=full_line
    )


def extract_cell_at_intersection(doc, col_channel, row_band, margin=1.0):
    """
    Extracts text and values at the 2D intersection of ColumnChannel and RowBand.
    Enforces strict vertical midpoint isolation to prevent adjacent row bleeding.
    Fails loudly on empty clip or ambiguous values.
    """
    p_idx = row_band.target_page - 1
    page = doc[p_idx]

    # Intersection rectangle
    clip_rect = fitz.Rect(
        col_channel.x0 - margin,
        row_band.y0 - margin,
        col_channel.x1 + margin,
        row_band.y1 + margin
    )

    clip_text = page.get_text("text", clip=clip_rect).strip()
    if not clip_text:
        raise EmptyCellError(
            f"Intersection clip {clip_rect} on page {row_band.target_page} is completely empty! "
            f"Row: '{row_band.name}', Col: '{col_channel.name}'"
        )

    all_words = page.get_text("words", clip=clip_rect)
    if not all_words:
        raise EmptyCellError(f"No words extracted in clip {clip_rect}")

    # STRICT VERTICAL MIDPOINT FILTER:
    # A word belongs to this row IF AND ONLY IF its vertical center lies within the row label band.
    # This prevents catching characters from the row above or below.
    row_y0 = row_band.row_rect.y0 - 2.0
    row_y1 = row_band.row_rect.y1 + 2.0
    words = [
        w for w in all_words
        if row_y0 <= (w[1] + w[3]) / 2.0 <= row_y1
    ]

    if not words:
        raise EmptyCellError(
            f"All words in clip {clip_rect} belonged to adjacent rows (outside vertical band [{row_y0:.1f}, {row_y1:.1f}])."
        )

    # Sort words left-to-right
    words.sort(key=lambda w: w[0])

    # Compute tight bounding box of filtered words
    x0_tight = min(w[0] for w in words)
    y0_tight = min(w[1] for w in words)
    x1_tight = max(w[2] for w in words)
    y1_tight = max(w[3] for w in words)
    tight_bbox = fitz.Rect(x0_tight, y0_tight, x1_tight, y1_tight)

    # Extract numerical tokens
    raw_str = " ".join(w[4] for w in words).strip()

    # Check for multiple distinct n(pct) groups on the same row (e.g. compound subcolumns)
    pct_matches = list(re.finditer(r"(\d+(?:\.\d+)?)\s*\(\s*(\d+(?:\.\d+)?)\s*%?\s*\)?", raw_str))

    if len(pct_matches) > 1:
        # Check if one is an event count (< 100%) and the other is denominator (100%)
        non_100 = [m for m in pct_matches if float(m.group(2)) != 100.0]
        if len(non_100) == 1:
            m_pct = non_100[0]
        else:
            raise AmbiguousCellError(
                f"Intersection contains {len(pct_matches)} distinct numerical cells: '{raw_str}'. "
                f"Specify subcol_query to disambiguate."
            )
    elif len(pct_matches) == 1:
        m_pct = pct_matches[0]
    else:
        m_pct = None

    if m_pct:
        n_val = float(m_pct.group(1)) if "." in m_pct.group(1) else int(m_pct.group(1))
        pct_val = float(m_pct.group(2))
        pct_raw_str = m_pct.group(2)
        if "." in pct_raw_str:
            pct_decimals = len(pct_raw_str.split(".")[1].rstrip("%").strip())
        else:
            pct_decimals = 0

        return {
            "n": n_val,
            "pct": pct_val,
            "pct_decimals": pct_decimals,
            "raw": raw_str,
            "bbox": tight_bbox,
            "clip_rect": clip_rect
        }

    # Check for standalone integer: e.g. "29"
    m_int = re.search(r"^(\d+)$", raw_str)
    if m_int:
        return {
            "n": int(m_int.group(1)),
            "pct": None,
            "pct_decimals": None,
            "raw": raw_str,
            "bbox": tight_bbox,
            "clip_rect": clip_rect
        }

    # Check for mean (SD): e.g. "39.1 (1.4)"
    m_mean = re.search(r"(\d+(?:\.\d+)?)\s*\(\s*(\d+(?:\.\d+)?)\s*\)", raw_str)
    if m_mean:
        return {
            "mean": float(m_mean.group(1)),
            "sd": float(m_mean.group(2)),
            "pct_decimals": None,
            "raw": raw_str,
            "bbox": tight_bbox,
            "clip_rect": clip_rect
        }

    return {
        "raw": raw_str,
        "n": None,
        "pct": None,
        "pct_decimals": None,
        "bbox": tight_bbox,
        "clip_rect": clip_rect
    }


# ==============================================================================
# 4. Pillar 2: Mathematical Checksum Invariance (Derived Precision Tolerance)
# ==============================================================================

def validate_math_checksum(n, reported_pct, group_N, pct_decimals=None, tolerance=None):
    """
    Verifies that reported percent matches n / N * 100 within precision tolerance.
    Derived tolerance formula:
      tol = 0.5 * 10^(-d) + 1e-9 percentage points,
      where d is the number of decimal places in the reported percentage string.
      - d = 0 (e.g. 68%):  tol = 0.5%
      - d = 1 (e.g. 26.1%): tol = 0.05%
      - d = 2 (e.g. 26.13%): tol = 0.005%

    Also computes discriminative power:
      - n_tolerance_window: [n_min, n_max] integer range of n producing this percentage
      - checksum_discriminates: True iff n_min == n_max == n.

    Fails loudly with MathChecksumError if invariant is violated.
    """
    if group_N is None or reported_pct is None or n is None:
        return {
            "status": "UNCHECKED",
            "reason": "Missing N, n, or reported percentage",
            "expected_pct": None,
            "reported_pct": reported_pct,
            "delta": None,
            "tolerance": None,
            "checksum_discriminates": False,
            "n_tolerance_window": None
        }

    if group_N <= 0:
        raise MathChecksumError(f"Invalid denominator group_N: {group_N}")

    # Determine number of decimal places d
    if tolerance is not None:
        tol = float(tolerance)
        d = 0
    else:
        if pct_decimals is not None:
            d = int(pct_decimals)
        else:
            if isinstance(reported_pct, (int, float)) and float(reported_pct) != float(int(reported_pct)):
                d = len(str(reported_pct).split(".")[1])
            else:
                d = 0
        tol = 0.5 * (10.0 ** (-d)) + 1e-9

    expected_pct = (n / group_N) * 100.0
    delta = abs(reported_pct - expected_pct)

    # Compute integer tolerance window for n: [n_min, n_max]
    pct_low = (reported_pct - tol) / 100.0
    pct_high = (reported_pct + tol) / 100.0
    n_min = math.ceil(pct_low * group_N - 1e-9)
    n_max = math.floor(pct_high * group_N + 1e-9)
    n_min = max(0, n_min)
    n_max = min(group_N, n_max)
    checksum_discriminates = (n_min == n_max == n)

    if delta > tol:
        raise MathChecksumError(
            f"Math Checksum Mismatch: {n} / {group_N} = {expected_pct:.3f}%, "
            f"reported is {reported_pct}% (delta = {delta:.4f}% > {tol:.4f}% precision tolerance [d={d}]!)"
        )

    return {
        "status": "PASS",
        "expected_pct": round(expected_pct, 3),
        "reported_pct": reported_pct,
        "delta": round(delta, 5),
        "tolerance": round(tol, 5),
        "decimals": d,
        "checksum_discriminates": checksum_discriminates,
        "n_tolerance_window": [n_min, n_max]
    }


# ==============================================================================
# 5. Tamper-Evidence Hashing, Human Confirmation & Visual Verification
# ==============================================================================

def compute_context_sha256(page, bbox, padding=25.0):
    """
    Computes tamper-evidence SHA-256 hash of the text surrounding bbox.
    """
    expanded = fitz.Rect(
        max(0.0, bbox.x0 - padding),
        max(0.0, bbox.y0 - padding),
        min(page.rect.width, bbox.x1 + padding),
        min(page.rect.height, bbox.y1 + padding)
    )
    context_text = page.get_text("text", clip=expanded).strip()
    return hashlib.sha256(context_text.encode("utf-8")).hexdigest()[:16]


def confirm_human_verification(datapoint, reviewer_name):
    """
    Explicit human confirmation action (Cochrane Chapter 5 requirement).
    Updates status from PENDING to CONFIRMED.
    The code NEVER sets this automatically.
    """
    if not reviewer_name or not str(reviewer_name).strip():
        raise ValueError("Reviewer name/ID is required for Cochrane human confirmation.")

    datapoint["human_confirmation"] = {
        "reviewer": str(reviewer_name).strip(),
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "CONFIRMED"
    }
    return datapoint


def check_human_confirmation_gate(datapoint):
    """
    Linter gate: Key clinical data cannot be synced to synthesis Excel while PENDING.
    Fails loudly with HumanConfirmationPendingError if unconfirmed.
    """
    conf = datapoint.get("human_confirmation", {})
    status = conf.get("status", "PENDING")
    if status != "CONFIRMED":
        raise HumanConfirmationPendingError(
            f"Datapoint '{datapoint.get('variable_canonical')}' for study '{datapoint.get('study_id')}' "
            f"is PENDING human confirmation (reviewer={conf.get('reviewer')}). "
            "Unconfirmed data cannot be exported to synthesis Excel under Cochrane standards."
        )
    return True


def render_verification_crop(doc, target_page_num, row_band, col_channel, cell_bbox, out_path=None):
    """
    Renders a visual PNG crop showing the cell, row header, and column channel.
    Provides inexpensive, auditable Cochrane-style human verification.
    """
    p_idx = target_page_num - 1
    page = doc[p_idx]

    # Crop rectangle covers row label to cell
    x0 = max(0.0, min(row_band.row_rect.x0, col_channel.x0) - 20)
    x1 = min(page.rect.width, max(col_channel.x1, cell_bbox.x1) + 20)
    y0 = max(0.0, row_band.y0 - 15)
    y1 = min(page.rect.height, row_band.y1 + 15)
    crop_rect = fitz.Rect(x0, y0, x1, y1)

    pix = page.get_pixmap(clip=crop_rect, dpi=150)
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        pix.save(out_path)
    return pix


# ==============================================================================
# 6. High-Level Extraction Entrypoint
# ==============================================================================

def extract_tabular_datapoint(doc, spec):
    """
    Orchestrates Pillar 1 & Pillar 2 extraction for a tabular clinical variable.
    spec dictionary:
      - 'study_id': str (optional, e.g. 'Perez_2023')
      - 'variable_canonical': str (optional, e.g. 'mortality_hyperglycemia_events')
      - 'header_page': int (1-indexed)
      - 'target_page': int (1-indexed)
      - 'col_query': str
      - 'subcol_query': str (optional)
      - 'row_query': str
      - 'parent_context': str (optional)
      - 'group_N': int (optional, for checksum)
      - 'tolerance': float (optional, overrides precision-derived tolerance)
    """
    # 1. Detect column channel (Pillar 1)
    col_ch = detect_column_channel(
        doc,
        header_page_num=spec["header_page"],
        col_query=spec["col_query"],
        subcol_query=spec.get("subcol_query")
    )

    # 2. Detect row band (Pillar 1)
    row_b = find_row_band(
        doc,
        target_page_num=spec["target_page"],
        row_query=spec["row_query"],
        parent_context=spec.get("parent_context")
    )

    # 3. Extract cell at 2D intersection
    cell_data = extract_cell_at_intersection(doc, col_ch, row_b)

    # 4. Validate mathematical checksum (Pillar 2)
    group_N = spec.get("group_N")
    checksum = validate_math_checksum(
        n=cell_data.get("n"),
        reported_pct=cell_data.get("pct"),
        group_N=group_N,
        pct_decimals=cell_data.get("pct_decimals"),
        tolerance=spec.get("tolerance")
    )

    # 5. Tamper-evidence hash
    target_page = doc[spec["target_page"] - 1]
    sha = compute_context_sha256(target_page, cell_data["bbox"])

    return {
        "status": "PASS",
        "study_id": spec.get("study_id", "Unknown"),
        "variable_canonical": spec.get("variable_canonical", spec["row_query"]),
        "value": cell_data.get("n", cell_data.get("mean", cell_data["raw"])),
        "pct": cell_data.get("pct"),
        "raw": cell_data["raw"],
        "bbox": [round(cell_data["bbox"].x0, 1), round(cell_data["bbox"].y0, 1),
                 round(cell_data["bbox"].x1, 1), round(cell_data["bbox"].y1, 1)],
        "col_channel": col_ch,
        "row_band": row_b,
        "checksum": checksum,
        "human_confirmation": {
            "reviewer": None,
            "timestamp": None,
            "status": "PENDING"
        },
        "tamper_sha256": sha
    }
