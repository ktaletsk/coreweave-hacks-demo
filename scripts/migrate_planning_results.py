# /// script
# requires-python = ">=3.13"
# dependencies = ["pandas>=2.2", "pyarrow>=19", "wandb==0.27.0"]
# ///
"""Import the original, recorded Gemma experiment into W&B Tables once.

This script makes no inference calls and never executes stored model code.
The presentation notebook subsequently reads only the versioned W&B Table.
"""

import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
import wandb

SOURCE_ID = "orbrx/wanderland-llm-planning"
SOURCE_REVISION = "be5cf953b11f36ad0a4a1149b2769e51aed32b81"
SOURCE_URL = (
    f"https://huggingface.co/datasets/{SOURCE_ID}/resolve/{SOURCE_REVISION}/"
    "data/train-00000-of-00001.parquet"
)
ARTIFACT_NAME = "can-llms-plan-original-results"
METHODS = {
    "plan_nothink": "plan · no-think",
    "plan_think": "plan · think",
    "code": "write code",
    "code_fb": "code + verifier",
}


def json_world(value):
    """Normalize a stored Python literal without evaluating executable code."""
    world = ast.literal_eval(value)
    for key in ("walls", "water", "lava"):
        world[key] = sorted(world[key])
    return json.dumps(world, sort_keys=True)


def prepare_results(parquet_bytes):
    frame = pd.read_parquet(io.BytesIO(parquet_bytes))
    if not frame.run_id.is_unique or not set(frame.method_label).issubset(METHODS):
        raise ValueError("Unexpected duplicate run IDs or method labels in the source.")
    # Keep all source fields, including raw outputs, timing, errors and hardware.
    frame["world_json"] = frame.world_repr.map(json_world)
    frame["approach"] = frame.method_label.map(METHODS)
    frame["source_revision"] = SOURCE_REVISION
    # Conversion makes arrays/scalars JSON-native and replaces missing values with null.
    records = json.loads(frame.to_json(orient="records"))
    return frame, records


def publish(frame, records, entity, project, directory):
    run_id = f"planning-import-{SOURCE_REVISION[:12]}"
    api = wandb.Api()
    try:
        previous = api.run(f"{entity}/{project}/{run_id}")
    except wandb.errors.CommError as error:
        if "could not find run" not in str(error).lower():
            raise
    else:
        raise RuntimeError(
            f"This source revision already has an import run: {previous.url}. "
            "Reuse its artifact instead of creating a duplicate."
        )
    columns = list(frame.columns)
    table = wandb.Table(columns=columns, data=[[r[c] for c in columns] for r in records])
    aggregate = frame.groupby(["method_label", "cols"], sort=True).agg(
        solved=("solved", "mean"), wall_time_s=("wall_time_s", "median"),
        output_tokens=("output_tokens", "median"), n=("solved", "size"),
    ).reset_index()
    metadata = {
        "source_dataset": SOURCE_ID, "source_revision": SOURCE_REVISION,
        "source_url": SOURCE_URL, "row_count": len(records),
        "experiment": "original-local-gemma", "model_id": frame.model_id.unique().tolist(),
        "hardware": frame.hardware.unique().tolist(),
        "note": "Historical local inference; timing does not measure W&B Inference or CoreWeave Sandboxes.",
    }
    with wandb.init(
        entity=entity, project=project, id=run_id, resume="never",
        name="Can LLMs Plan · original Gemma results", job_type="evaluation-import",
        config=metadata, tags=["can-llms-plan", "historical-results"],
        dir=str(directory), save_code=False,
    ) as run:
        artifact = wandb.Artifact(ARTIFACT_NAME, type="evaluation", metadata=metadata)
        artifact.add(table, "planning_results")
        logged = run.log_artifact(artifact)
        run.log({"planning_results": table, "results_by_grid": wandb.Table(dataframe=aggregate)})
        for metric, title in (
            ("solved", "Success vs. grid size"),
            ("wall_time_s", "Median wall-time vs. grid size"),
            ("output_tokens", "Median output tokens vs. grid size"),
        ):
            groups = [aggregate[aggregate.method_label == method] for method in METHODS]
            run.log({metric + "_by_grid": wandb.plot.line_series(
                xs=[group.cols.tolist() for group in groups],
                ys=[group[metric].tolist() for group in groups],
                keys=list(METHODS.values()), title=title, xname="Grid size",
            )})
        for method in METHODS:
            rows = frame[frame.method_label == method]
            run.summary.update({
                f"{method}/runs": len(rows), f"{method}/success_rate": float(rows.solved.mean()),
                f"{method}/median_wall_time_s": float(rows.wall_time_s.median()),
                f"{method}/median_output_tokens": float(rows.output_tokens.median()),
            })
        logged.wait()
        manifest = {**metadata, "artifact_ref": f"{entity}/{project}/{logged.name}", "run_url": run.url}
    # Read back the exact version to catch serialization or incomplete-upload problems.
    restored = api.artifact(manifest["artifact_ref"]).get("planning_results")
    if restored.columns != columns or len(restored.data) != len(records):
        raise RuntimeError("W&B Table round-trip changed the schema or row count.")
    if restored.data != [[r[c] for c in columns] for r in records]:
        raise RuntimeError("W&B Table round-trip changed recorded result values.")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entity", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with urlopen(SOURCE_URL, timeout=60) as response:
        payload = response.read()
    frame, records = prepare_results(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    manifest = publish(frame, records, args.entity, args.project, args.output.parent)
    manifest["source_file_sha256"] = hashlib.sha256(payload).hexdigest()
    args.output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
