#!/usr/bin/env python3
"""
Cross-reference railway data from spreadsheet with railway_timeline.json
to create multi-railway entries for settlements.

This script:
1. Parses Railway_lines column from UrbanSaskHist spreadsheet
2. Normalizes railway names to match existing categories
3. Looks up arrival years from railway_timeline.json
4. Creates updated railway_timeline.json with complete data
"""

import json
import pandas as pd
import re
import os

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
SPREADSHEET = os.path.join(os.path.dirname(PROJECT_DIR), "KnowledgeGraph", "UrbanSaskHist_Update_Jan_2026.xlsx")
TIMELINE_FILE = os.path.join(PROJECT_DIR, "data", "railway_timeline.json")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "data", "railway_timeline.json")

# Railway name normalization mapping
RAILWAY_ALIASES = {
    'CPR': 'CPR',
    'QLSRSC': 'QLSRSC',
    'CNoR': 'CNoR',
    'CNOR': 'CNoR',
    'GTPR': 'GTPR',
    'GTP': 'GTPR',
    'GPTR': 'GTPR',  # Typo in data
    'CN': 'Other',   # Post-1918 consolidation
    'SOO': 'Other',  # Soo Line
    'M&NW': 'Other', # Manitoba & North Western
    'M': 'Other',    # Manitoba railway
}

# Known arrival years for major multi-railway settlements
# Sources: Historical records, railway company histories
KNOWN_RAILWAY_YEARS = {
    # Saskatoon - major junction
    ('Saskatoon', 'QLSRSC'): 1890,
    ('Saskatoon', 'CNoR'): 1905,
    ('Saskatoon', 'GTPR'): 1908,

    # Regina - capital city
    ('Regina', 'CPR'): 1882,
    ('Regina', 'QLSRSC'): 1889,
    ('Regina', 'CNoR'): 1906,
    ('Regina', 'GTPR'): 1911,

    # Prince Albert - northern hub
    ('Prince Albert', 'QLSRSC'): 1890,
    ('Prince Albert', 'CNoR'): 1906,

    # Moose Jaw - CPR division point
    ('Moosejaw', 'CPR'): 1882,
    ('Moosejaw', 'CNoR'): 1908,
    ('Moosejaw', 'GTPR'): 1912,

    # Weyburn - southeastern hub
    ('Weyburn', 'CPR'): 1893,
    ('Weyburn', 'CNoR'): 1910,

    # Yorkton - eastern hub
    ('Yorkton', 'Other'): 1889,  # M&NW
    ('Yorkton', 'CPR'): 1890,
    ('Yorkton', 'GTPR'): 1908,

    # Melville - GTPR division point
    ('Melville', 'GTPR'): 1908,

    # Biggar - CPR/GTPR junction
    ('Biggar', 'CPR'): 1907,
    ('Biggar', 'GTPR'): 1910,

    # Nokomis - CPR/GTPR crossing
    ('Nokomis', 'CPR'): 1907,
    ('Nokomis', 'GTPR'): 1908,

    # Rosthern - QLSRSC line
    ('Rosthern', 'QLSRSC'): 1890,
    ('Rosthern', 'CNoR'): 1906,  # Took over from CPR

    # Lloydminster - CNoR main line
    ('Lloydminster (pt)', 'CNoR'): 1905,

    # Estevan - southeastern
    ('Estevan', 'CPR'): 1892,

    # Bienfait - from spreadsheet notes
    ('Bienfait', 'CPR'): 1905,
    ('Bienfait', 'CNoR'): 1909,

    # Craven - QLSRSC branch
    ('Craven', 'QLSRSC'): 1885,
}


def normalize_railway(name):
    """Normalize railway name to standard category."""
    name = name.strip().upper()
    # Remove common suffixes/notes
    name = re.sub(r'\s*\(.*\)', '', name)  # Remove parenthetical notes
    name = name.strip()

    return RAILWAY_ALIASES.get(name, RAILWAY_ALIASES.get(name.upper(), None))


def parse_railway_lines(railway_str):
    """Parse the Railway_lines field to extract individual railways."""
    if pd.isna(railway_str) or not railway_str:
        return []

    # Handle special cases with explanatory text
    railway_str = str(railway_str)

    # Skip entries that are clearly just notes
    if railway_str.lower().startswith('no ') or 'no information' in railway_str.lower():
        return []

    railways = []

    # Split by comma, but be careful with parenthetical notes
    # First, temporarily replace commas inside parentheses
    temp_str = railway_str
    paren_contents = re.findall(r'\([^)]+\)', temp_str)
    for i, content in enumerate(paren_contents):
        temp_str = temp_str.replace(content, f'__PAREN{i}__')

    # Now split by comma
    parts = temp_str.split(',')

    for part in parts:
        # Restore parentheses for context (but we'll strip them for the railway name)
        for i, content in enumerate(paren_contents):
            part = part.replace(f'__PAREN{i}__', content)

        # Extract railway name (before any parenthetical note)
        match = re.match(r'^([A-Za-z&]+)', part.strip())
        if match:
            railway_name = match.group(1).strip()
            normalized = normalize_railway(railway_name)
            if normalized and normalized not in railways:
                railways.append(normalized)

    return railways


def load_existing_timeline():
    """Load existing railway_timeline.json and build lookup dict."""
    with open(TIMELINE_FILE, 'r') as f:
        timeline = json.load(f)

    # Build lookup: (settlement_name, railway) -> year
    lookup = {}
    for railway, settlements in timeline.items():
        for s in settlements:
            lookup[(s['name'], railway)] = s['year']

    return timeline, lookup


def main():
    print("Loading data...")

    # Load spreadsheet
    df = pd.read_excel(SPREADSHEET)
    print(f"Loaded {len(df)} settlements from spreadsheet")

    # Load existing timeline
    existing_timeline, year_lookup = load_existing_timeline()
    print(f"Loaded existing timeline with {sum(len(v) for v in existing_timeline.values())} entries")

    # Parse railways from spreadsheet
    print("\nParsing Railway_lines column...")
    settlement_railways = {}
    parse_issues = []

    for _, row in df.iterrows():
        settlement = row['PR_CD_CSD']
        railway_str = row['Railway_lines']
        first_year = row['Railway_arrives']

        railways = parse_railway_lines(railway_str)

        if railways:
            settlement_railways[settlement] = {
                'railways': railways,
                'first_year': int(first_year) if pd.notna(first_year) else None,
                'raw': railway_str
            }

    print(f"Parsed railways for {len(settlement_railways)} settlements")

    # Count multi-railway settlements
    multi_railway = sum(1 for s in settlement_railways.values() if len(s['railways']) > 1)
    print(f"Settlements with multiple railways: {multi_railway}")

    # Cross-reference with existing timeline to get years
    print("\nCross-referencing with existing timeline and known years...")

    # Build new timeline structure
    new_timeline = {railway: [] for railway in ['QLSRSC', 'CPR', 'CNoR', 'GTPR', 'Other']}

    matched_existing = 0
    matched_known = 0
    used_first_year = 0
    unmatched = 0

    for settlement, data in settlement_railways.items():
        for i, railway in enumerate(data['railways']):
            year = None

            # Priority 1: Check known railway years (manually researched)
            if (settlement, railway) in KNOWN_RAILWAY_YEARS:
                year = KNOWN_RAILWAY_YEARS[(settlement, railway)]
                matched_known += 1
            # Priority 2: Check existing timeline
            elif (settlement, railway) in year_lookup:
                year = year_lookup[(settlement, railway)]
                matched_existing += 1
            # Priority 3: Use first_year from spreadsheet for the first railway
            elif i == 0 and data['first_year']:
                year = data['first_year']
                used_first_year += 1
            else:
                # No year found
                unmatched += 1
                continue

            # Add to new timeline (avoid duplicates)
            existing_names = [s['name'] for s in new_timeline[railway]]
            if settlement not in existing_names:
                new_timeline[railway].append({
                    'name': settlement,
                    'year': year
                })

    print(f"Matched from known years (researched): {matched_known}")
    print(f"Matched from existing timeline: {matched_existing}")
    print(f"Used first_year from spreadsheet: {used_first_year}")
    print(f"Unmatched (no year available): {unmatched}")

    # Sort each railway's settlements by year
    for railway in new_timeline:
        new_timeline[railway].sort(key=lambda x: (x['year'], x['name']))

    # Print summary
    print("\nNew timeline summary:")
    for railway, settlements in new_timeline.items():
        print(f"  {railway}: {len(settlements)} settlements")

    # Show settlements that now have multiple railways
    print("\nSample multi-railway settlements (with years):")
    shown = 0
    for settlement, data in settlement_railways.items():
        if len(data['railways']) > 1:
            railways_with_years = []
            for i, railway in enumerate(data['railways']):
                # Same lookup logic as above
                year = KNOWN_RAILWAY_YEARS.get((settlement, railway))
                if not year:
                    year = year_lookup.get((settlement, railway))
                if not year and i == 0 and data['first_year']:
                    year = data['first_year']
                if year:
                    railways_with_years.append(f"{railway}({year})")
                else:
                    railways_with_years.append(f"{railway}(?)")
            print(f"  {settlement}: {', '.join(railways_with_years)}")
            shown += 1
            if shown >= 15:
                break

    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(new_timeline, f, indent=2)

    print(f"\nOutput written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
