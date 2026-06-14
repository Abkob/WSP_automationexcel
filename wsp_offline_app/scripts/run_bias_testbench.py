"""
Semantic search bias testbench.

Checks whether the AI search is unfairly returning the same pool of students
regardless of the query, and diagnoses the root cause.

Run from the project root:
    python scripts/run_bias_testbench.py
"""
from __future__ import annotations

import sys
import os
import collections
import statistics

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AppSettings
from database.db import create_sqlite_engine, initialize_database
from database.models import StudentCurrent
from services.embedding_service import get_default_embedding_model
from services.filter_service import SemanticFilter
from services.semantic_document_service import (
    SEMANTIC_PROFILE_FIELDS,
    build_student_semantic_profile,
    build_student_semantic_profiles,
)
from services.semantic_search_service import get_default_vector_store, rank_student_rows_by_vector_search
from sqlalchemy.orm import Session

DIVIDER = "-" * 70

# Diverse queries that should return different student populations
QUERIES = [
    "software developer with Python programming skills",
    "graphic design and visual arts creative student",
    "lab assistant biology chemistry science",
    "finance accounting business economics",
    "event planning organization communication",
    "Arabic French English multilingual languages",
    "student on probation needing financial support",
    "senior student high GPA academic excellence",
    "social media marketing digital content",
    "engineering mathematics problem solving",
    "healthcare nursing medical sciences",
    "education teaching tutoring mentoring",
]

WSP_FIELDS = (
    "WSP_TECHNICAL_SKILLS",
    "WSP_ORGANIZATIONAL_SKILLS",
    "WSP_INTERPERSONAL_SKILLS",
    "WSP_ADDITIONAL_SKILLS",
    "WSP_PREVIOUS_TYPE_OF_WORK",
    "WSP_PREFERRED_TYPE_OF_WORK",
    "WSP_PREV_WORK",
    "WSP_WRITTEN_LANGUAGES",
    "WSP_SPOKEN_LANGUAGES",
)


def section(title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def main() -> None:
    settings = AppSettings()
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)

    with Session(engine) as session:
        total = session.query(StudentCurrent).count()

    print(f"\nWSP Semantic Search Bias Test")
    print(f"Total students in DB: {total}")

    # ── 1. Index coverage ────────────────────────────────────────────────────
    section("1. FAISS Index Coverage")
    store = get_default_vector_store(settings)
    indexed_ids = store.record_ids()
    indexed_count = len(indexed_ids)

    with Session(engine) as session:
        db_ids = {r.STUD_ID for r in session.query(StudentCurrent.STUD_ID)}

    in_index_not_db = indexed_ids - db_ids
    in_db_not_index = db_ids - indexed_ids

    print(f"Students in DB:    {len(db_ids)}")
    print(f"Students in index: {indexed_count}")
    print(f"Coverage:          {indexed_count / max(len(db_ids), 1) * 100:.1f}%")
    if in_db_not_index:
        print(f"NOT in index:      {len(in_db_not_index)} students  ← these can never appear in AI search")
        sample = sorted(in_db_not_index)[:5]
        print(f"  Sample IDs: {sample}")
    else:
        print("All students are indexed ✓")
    if in_index_not_db:
        print(f"Stale (in index but not DB): {len(in_index_not_db)}")

    # ── 2. Profile completeness ───────────────────────────────────────────────
    section("2. Profile Completeness (WSP skills data)")
    with Session(engine) as session:
        all_students = tuple(session.query(StudentCurrent).all())

    empty_profiles = 0
    sparse_profiles = 0   # have some academic data but NO WSP-specific fields
    full_profiles = 0
    profile_texts: list[str] = []

    for s in all_students:
        has_wsp = any(
            str(getattr(s, f, "") or "").strip()
            for f in WSP_FIELDS
        )
        profile = build_student_semantic_profile(s)
        profile_texts.append(profile.text)
        if not has_wsp:
            sparse_profiles += 1
        else:
            full_profiles += 1

    print(f"Students with WSP skills/work data: {full_profiles}  ({full_profiles/max(total,1)*100:.1f}%)")
    print(f"Students with ONLY academic data:   {sparse_profiles}  ({sparse_profiles/max(total,1)*100:.1f}%)")
    print()
    print("  ↳ Students without WSP data have near-identical profile text.")
    print("    When many share the same major/class, their embedding vectors are")
    print("    almost indistinguishable — and the record_id tiebreaker always")
    print("    returns the same ones alphabetically.")

    # ── 3. Profile text uniqueness ────────────────────────────────────────────
    section("3. Profile Text Uniqueness")
    unique_texts = len(set(profile_texts))
    duplicates = total - unique_texts
    text_counts = collections.Counter(profile_texts)
    top_duplicated = text_counts.most_common(5)

    print(f"Unique profile texts: {unique_texts} / {total}")
    print(f"Exact duplicates:     {duplicates} students share a profile text with at least one other")
    if top_duplicated:
        print("\nMost common profile texts (shared by N students):")
        for text, count in top_duplicated:
            preview = text.replace("\n", " ")[:120]
            print(f"  [{count} students] {preview}…")

    # ── 4. Score distribution across all queries ──────────────────────────────
    section("4. Score Distribution Per Query (top_k=100, threshold=0.0)")
    model = get_default_embedding_model(settings)

    seen_ids: dict[str, set[str]] = {}
    all_seen: set[str] = set()

    with Session(engine) as session:
        all_rows = tuple(session.query(StudentCurrent).all())

    for query in QUERIES:
        sf = SemanticFilter(query, top_k=100, minimum_score=0.0)
        with Session(engine) as session:
            matches = rank_student_rows_by_vector_search(
                settings, session, sf, all_rows,
                embedding_model=model, vector_store=store,
            )
        ids = {m.STUD_ID for m in matches}
        scores = [m.score for m in matches]
        seen_ids[query] = ids
        all_seen |= ids

        if scores:
            score_min = min(scores)
            score_max = max(scores)
            score_mean = statistics.mean(scores)
            score_p25 = sorted(scores)[len(scores) // 4]
            score_p75 = sorted(scores)[len(scores) * 3 // 4]
            near_tie = sum(1 for s in scores if abs(s - score_max) < 0.001)
        else:
            score_min = score_max = score_mean = score_p25 = score_p75 = 0.0
            near_tie = 0

        print(f"\n  Query: \"{query[:55]}\"")
        print(f"    Returned: {len(matches)} students | "
              f"score range [{score_min:.4f} – {score_max:.4f}] | "
              f"mean={score_mean:.4f}")
        print(f"    Near-tied at top (Δ<0.001): {near_tie} students (tiebreaker = record_id alphabetical)")

    # ── 5. Cross-query diversity ───────────────────────────────────────────────
    section("5. Cross-Query Diversity")
    print(f"Queries run: {len(QUERIES)}")
    print(f"Total unique students seen across ALL queries (top_k=100): {len(all_seen)} / {total}")
    print(f"Never returned by any query: {total - len(all_seen)} students")

    # Frequency: how many queries did each student appear in?
    id_frequency: dict[str, int] = collections.defaultdict(int)
    for ids in seen_ids.values():
        for sid in ids:
            id_frequency[sid] += 1

    freq_counts = collections.Counter(id_frequency.values())
    print("\nAppearance frequency across queries:")
    for freq in sorted(freq_counts):
        count = freq_counts[freq]
        pct = count / max(total, 1) * 100
        bar = "#" * min(40, int(pct * 2))
        print(f"  Appeared in {freq:2d}/{len(QUERIES)} queries: {count:4d} students ({pct:.1f}%) {bar}")

    always_present = [sid for sid, freq in id_frequency.items() if freq == len(QUERIES)]
    never_present  = [sid for sid in db_ids if id_frequency[sid] == 0]
    print(f"\nAlways in top-100 regardless of query: {len(always_present)} students  ← BIAS CANDIDATES")
    print(f"Never returned by any query:           {len(never_present)} students  ← INVISIBLE TO AI SEARCH")

    if always_present:
        with Session(engine) as session:
            sticky = (
                session.query(StudentCurrent)
                .filter(StudentCurrent.STUD_ID.in_(always_present[:10]))
                .all()
            )
        print("\nSample always-present students (first 10):")
        for s in sticky:
            has_wsp = any(str(getattr(s, f, "") or "").strip() for f in WSP_FIELDS)
            print(f"  {s.STUD_ID} | {getattr(s,'MAJR_DESC','')[:30]} | GPA={getattr(s,'CUM_GPA','')} | WSP data={'yes' if has_wsp else 'NO'}")

    # ── 6. Verdict ────────────────────────────────────────────────────────────
    section("6. Diagnosis & Recommendations")

    issues: list[str] = []
    if in_db_not_index:
        issues.append(f"INDEX INCOMPLETE: {len(in_db_not_index)} students missing from FAISS index")
    if duplicates > total * 0.3:
        issues.append(f"PROFILE DEDUPLICATION: {duplicates} students ({duplicates/max(total,1)*100:.0f}%) share identical profile text → identical vectors → tiebreaker bias")
    if sparse_profiles > total * 0.5:
        issues.append(f"SPARSE DATA: {sparse_profiles/max(total,1)*100:.0f}% of students have no WSP skills data → cluster together → same students always returned")
    if always_present and len(always_present) > 10:
        issues.append(f"STICKY STUDENTS: {len(always_present)} students appear in every query's top-100 → strong alphabetical tiebreaker bias")

    if issues:
        print("ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
        print("ROOT CAUSE SUMMARY:")
        print("  Students without WSP data have near-identical profile text.")
        print("  mxbai embeds them to nearly-identical vectors.")
        print("  Score ties are broken by record_id (alphabetical), so")
        print("  the SAME students always win ties, regardless of the query.")
        print()
        print("RECOMMENDED FIXES:")
        print("  A. Change tiebreaker from record_id to random shuffle (biggest impact)")
        print("  B. Lower minimum_score threshold so more students are eligible")
        print("  C. Add a small random noise term to scores of students with")
        print("     no WSP data to break deterministic ties")
        print("  D. Exclude students from semantic results if their profile is")
        print("     purely academic (no WSP fields) — only return them via")
        print("     regular filters, not AI matching")
    else:
        print("No significant bias detected.")
        print(f"Diversity looks healthy: {len(all_seen)} unique students seen across {len(QUERIES)} queries.")

    print(f"\n{DIVIDER}\n")


if __name__ == "__main__":
    main()
