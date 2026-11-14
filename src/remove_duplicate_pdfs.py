#!/usr/bin/env python3
"""
remove_duplicate_pdfs.py
Safely removes redundant duplicate PDF files from data/pdfs/stewardship_candidates_394:
1. Exact hash matches: keeps canonical, deletes duplicate.
2. Suffix duplicates: removes ' (1).pdf', ' (2).pdf' where base exists.
"""
import os
import sys
import glob
import hashlib
import re

def compute_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    pdf_dir = r'data\pdfs\stewardship_candidates_394'
    all_files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
    initial_count = len(all_files)
    print(f"Initial PDF count: {initial_count}")

    # 1. Exact hash mapping
    hash_to_files = {}
    for p in all_files:
        sha = compute_hash(p)
        hash_to_files.setdefault(sha, []).append(p)

    deleted_files = []
    
    # Process exact hash duplicates
    for sha, paths in hash_to_files.items():
        if len(paths) > 1:
            # Sort paths so cleaner / canonical name is kept first
            # e.g., 'file.pdf' before 'file (1).pdf'
            def sort_key(p):
                fn = os.path.basename(p)
                has_paren = 1 if re.search(r'\s*\(\d+\)\.pdf$', fn) else 0
                has_extra_digit = 1 if re.search(r'\d{2,}\.pdf$', fn) and not fn.isdigit() else 0
                length = len(fn)
                return (has_paren, has_extra_digit, length, fn)

            sorted_paths = sorted(paths, key=sort_key)
            canonical = sorted_paths[0]
            to_remove = sorted_paths[1:]

            for r in to_remove:
                if os.path.exists(r):
                    os.remove(r)
                    deleted_files.append((os.path.basename(r), os.path.basename(canonical), "Exact hash match"))

    # 2. Check remaining suffix duplicates like 'file (1).pdf' where base exists
    remaining_files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
    for p in remaining_files:
        fn = os.path.basename(p)
        if ' (1).pdf' in fn or ' (2).pdf' in fn:
            clean_name = re.sub(r'\s*\(\d+\)\.pdf$', '.pdf', fn)
            clean_path = os.path.join(pdf_dir, clean_name)
            if os.path.exists(clean_path) and clean_path != p:
                if os.path.exists(p):
                    os.remove(p)
                    deleted_files.append((fn, clean_name, "Filename suffix copy"))

    # 3. Final verification
    final_files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
    final_count = len(final_files)

    print(f"\n==========================================")
    print(f"DUPLICATE REMOVAL REPORT")
    print(f"==========================================")
    print(f"Initial files: {initial_count}")
    print(f"Deleted duplicate files: {len(deleted_files)}")
    print(f"Remaining unique files: {final_count}")
    print(f"Expected count ({initial_count} - {len(deleted_files)}): {initial_count - len(deleted_files)}")
    print(f"==========================================")

    for del_fn, orig_fn, reason in deleted_files:
        print(f"  [-] Deleted: {del_fn} (Kept: {orig_fn}) [{reason}]")

if __name__ == '__main__':
    main()

