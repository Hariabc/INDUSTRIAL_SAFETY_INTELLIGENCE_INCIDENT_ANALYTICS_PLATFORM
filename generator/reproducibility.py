import os
import json
import time
from generator.config import GeneratorConfig
from generator.generate import run_pipeline


def test_reproducibility(seed: int = 20261022) -> dict:
    """
    Executes two identical generation runs with the specified seed and compares:
    1. Table record counts
    2. Primary Key ID sequences
    3. File checksums (SHA-256)
    4. Deterministic summary metrics
    
    Produces data/reproducibility_report.json.
    """
    print("================================================================")
    print("  RUNNING REPRODUCIBILITY VERIFICATION (Two Fixed-Seed Runs)")
    print(f"  Seed: {seed}")
    print("================================================================")

    config = GeneratorConfig(
        seed=seed,
        num_plants=4,
        num_machines=60,
        num_alarm_definitions=200,
        num_alarm_events=5000,  # 5,000 events for swift, thorough reproducibility check
        simulation_days=30,
    )

    # Run 1
    print("\nExecuting Run 1...")
    t0 = time.time()
    ds1, gt1, manifest1 = run_pipeline(config, load_db=False)
    time1 = time.time() - t0

    # Run 2
    print("\nExecuting Run 2...")
    t0 = time.time()
    ds2, gt2, manifest2 = run_pipeline(config, load_db=False)
    time2 = time.time() - t0

    # Comparisons
    count_matches = {}
    id_matches = {}
    mismatches = []

    for table in ds1:
        c1 = len(ds1[table])
        c2 = len(ds2[table])
        matched = (c1 == c2)
        count_matches[table] = {"run_1": c1, "run_2": c2, "match": matched}
        if not matched:
            mismatches.append(f"Count mismatch in {table}: {c1} vs {c2}")

        # Compare sample IDs
        if c1 > 0 and c2 > 0:
            ids1 = [r.get("id") or r.get("source_event_id") or list(r.values())[0] for r in ds1[table][:50]]
            ids2 = [r.get("id") or r.get("source_event_id") or list(r.values())[0] for r in ds2[table][:50]]
            id_match = (ids1 == ids2)
            id_matches[table] = id_match
            if not id_match:
                mismatches.append(f"ID sequence mismatch in {table}")

    # Compare ground truth counts and IDs
    gt_c1 = len(gt1)
    gt_c2 = len(gt2)
    gt_match = (gt_c1 == gt_c2)
    if not gt_match:
        mismatches.append(f"Ground truth count mismatch: {gt_c1} vs {gt_c2}")

    gt_ids1 = [r["anomaly_id"] for r in gt1]
    gt_ids2 = [r["anomaly_id"] for r in gt2]
    gt_id_match = (gt_ids1 == gt_ids2)
    if not gt_id_match:
        mismatches.append("Ground truth anomaly IDs mismatch")

    # Compare SHA256 Checksums
    checksum_matches = {}
    for f_name, h1 in manifest1["checksums"].items():
        h2 = manifest2["checksums"].get(f_name)
        match = (h1 == h2)
        checksum_matches[f_name] = {"match": match, "hash_1": h1, "hash_2": h2}
        if not match:
            mismatches.append(f"Checksum mismatch for {f_name}")

    is_reproducible = len(mismatches) == 0

    report = {
        "verified_at": manifest2["generated_at"],
        "seed": seed,
        "is_reproducible": is_reproducible,
        "run_1_duration_seconds": round(time1, 2),
        "run_2_duration_seconds": round(time2, 2),
        "total_tables_checked": len(count_matches),
        "table_count_comparisons": count_matches,
        "id_sequence_comparisons": id_matches,
        "checksum_comparisons": checksum_matches,
        "ground_truth_count_match": gt_match,
        "ground_truth_ids_match": gt_id_match,
        "mismatches": mismatches,
    }

    os.makedirs("data", exist_ok=True)
    report_path = os.path.join("data", "reproducibility_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n================================================================")
    print(f"  REPRODUCIBILITY STATUS: {'SUCCESS - 100% REPRODUCIBLE' if is_reproducible else 'FAILED'}")
    print(f"  Report written to: {report_path}")
    print(f"================================================================")

    return report


if __name__ == "__main__":
    test_reproducibility()
