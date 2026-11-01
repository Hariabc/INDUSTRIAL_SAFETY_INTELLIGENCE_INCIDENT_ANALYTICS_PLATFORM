import os
import json
import csv
import hashlib
from datetime import datetime
from typing import Dict, List, Any


class DataExporter:
    """Exports generated synthetic datasets to CSV, JSON, SQL seed, and manifest."""

    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        self.csv_dir = os.path.join(output_dir, "exports", "csv")
        self.json_dir = os.path.join(output_dir, "exports", "json")
        self.sql_dir = os.path.join(output_dir, "exports", "sql")

        for d in [self.csv_dir, self.json_dir, self.sql_dir]:
            os.makedirs(d, exist_ok=True)

    def export_all(
        self,
        datasets: Dict[str, List[dict]],
        ground_truth: List[dict],
        config: Any,
        generation_duration_sec: float
    ) -> Dict[str, Any]:
        """Export all datasets to CSV, JSON, SQL, and manifest."""
        manifest = {
            "platform_name": "Industrial Safety Intelligence Platform",
            "generator_version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat(),
            "duration_seconds": round(generation_duration_sec, 2),
            "config": {
                "seed": config.seed,
                "plants": config.num_plants,
                "machines": config.num_machines,
                "alarm_definitions": config.num_alarm_definitions,
                "alarm_events_requested": config.num_alarm_events,
                "simulation_days": config.simulation_days,
                "start_date": config.start_date.isoformat(),
            },
            "tables": {},
            "checksums": {},
        }

        # 1. Export CSV and JSON for each entity
        for table_name, records in datasets.items():
            if not records:
                continue

            csv_path = os.path.join(self.csv_dir, f"{table_name}.csv")
            json_path = os.path.join(self.json_dir, f"{table_name}.json")

            # Write CSV
            fieldnames = list(records[0].keys())
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in records:
                    # Format datetimes
                    row = {
                        k: (v.isoformat() if isinstance(v, datetime) else v)
                        for k, v in r.items()
                    }
                    writer.writerow(row)

            # Write JSON
            with open(json_path, "w", encoding="utf-8") as f:
                serialized = [
                    {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in r.items()}
                    for r in records
                ]
                json.dump(serialized, f, indent=2)

            # Calculate SHA256 checksum
            with open(csv_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            manifest["tables"][table_name] = {
                "count": len(records),
                "csv_path": csv_path,
                "json_path": json_path,
                "sha256": file_hash,
            }
            manifest["checksums"][f"{table_name}.csv"] = file_hash

        # 2. Export Ground Truth strictly separately
        gt_csv_path = os.path.join(self.output_dir, "ground_truth.csv")
        gt_json_path = os.path.join(self.output_dir, "ground_truth.json")

        if ground_truth:
            gt_fieldnames = list(ground_truth[0].keys())
            with open(gt_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=gt_fieldnames)
                writer.writeheader()
                writer.writerows(ground_truth)

            with open(gt_json_path, "w", encoding="utf-8") as f:
                json.dump(ground_truth, f, indent=2)

            with open(gt_csv_path, "rb") as f:
                gt_hash = hashlib.sha256(f.read()).hexdigest()

            manifest["ground_truth"] = {
                "count": len(ground_truth),
                "csv_path": gt_csv_path,
                "json_path": gt_json_path,
                "sha256": gt_hash,
            }
            manifest["checksums"]["ground_truth.csv"] = gt_hash

        # 3. Write Source Manifest
        manifest_path = os.path.join(self.output_dir, "source_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # 4. Generate SQL Seed file
        self._generate_sql_seed(datasets)

        return manifest

    def _generate_sql_seed(self, datasets: Dict[str, List[dict]]):
        """Generate a portable SQL insert script for relational seeding."""
        sql_path = os.path.join(self.sql_dir, "seed_data.sql")
        # Only seed core parent entities in SQL script to keep file size reasonable
        core_tables = [
            "plants", "safety_zones", "machines", "machine_safety_zones",
            "interlocks", "alarm_definitions"
        ]

        with open(sql_path, "w", encoding="utf-8") as f:
            f.write("-- Industrial Safety Intelligence Platform - Core Seed Data\n")
            f.write(f"-- Generated: {datetime.utcnow().isoformat()}\n\n")

            for tbl in core_tables:
                records = datasets.get(tbl, [])
                if not records:
                    continue
                f.write(f"-- Table: {tbl} ({len(records)} rows)\n")
                cols = list(records[0].keys())
                col_str = ", ".join(cols)

                for r in records:
                    vals = []
                    for c in cols:
                        v = r[c]
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        elif isinstance(v, bool):
                            vals.append("TRUE" if v else "FALSE")
                        elif isinstance(v, datetime):
                            vals.append(f"'{v.isoformat()}'")
                        else:
                            clean_str = str(v).replace("'", "''")
                            vals.append(f"'{clean_str}'")
                    val_str = ", ".join(vals)
                    f.write(f"INSERT INTO {tbl} ({col_str}) VALUES ({val_str});\n")
                f.write("\n")
