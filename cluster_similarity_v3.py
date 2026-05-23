"""
Build phraseologisms_with_similarity_v3.db.

Stricter rule: two rows belong to the same cluster only when BOTH
`phrase` and `definition` are similar (so similar that the rows are
hard to tell apart).

Method:
- Embed `phrase` and `definition` separately with the same multilingual
  sentence-transformer model.
- For each pair (i, j) compute cos_sim_phrase and cos_sim_def.
- Combined similarity = min(cos_sim_phrase, cos_sim_def). Using min
  forces BOTH signals to be high simultaneously.
- Complete-linkage agglomerative clustering on combined distance.
- Threshold MIN_SIM = 0.78 (i.e. both phrase_sim >= 0.78 AND
  def_sim >= 0.78 for every pair inside a cluster).
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
import uuid
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sentence_transformers import SentenceTransformer

SRC_DB = Path("phraseologisms.db")
DST_DB = Path("phraseologisms_with_similarity_v3.db")
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
MIN_SIM = 0.78
DIST_THRESHOLD = 1.0 - MIN_SIM


def main() -> int:
    if not SRC_DB.exists():
        print(f"Source DB not found: {SRC_DB}", file=sys.stderr)
        return 1

    print(f"Copying {SRC_DB} -> {DST_DB}")
    shutil.copyfile(SRC_DB, DST_DB)

    conn = sqlite3.connect(DST_DB)
    cur = conn.cursor()

    cols = [r[1] for r in cur.execute("PRAGMA table_info(phraseologisms)").fetchall()]
    if "similarity" not in cols:
        cur.execute("ALTER TABLE phraseologisms ADD COLUMN similarity TEXT")
        conn.commit()

    rows = cur.execute(
        "SELECT id, phrase, definition FROM phraseologisms ORDER BY id"
    ).fetchall()
    ids = [r[0] for r in rows]
    phrases = [(r[1] or "").strip() for r in rows]
    definitions = [(r[2] or "").strip() for r in rows]
    n = len(rows)
    print(f"Loaded {n} rows")

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print("Encoding phrases...")
    emb_p = model.encode(
        phrases,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    print("Encoding definitions...")
    emb_d = model.encode(
        definitions,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    print("Computing similarity matrices...")
    sim_p = emb_p @ emb_p.T
    sim_d = emb_d @ emb_d.T
    sim_min = np.minimum(sim_p, sim_d)

    dist = 1.0 - sim_min
    np.fill_diagonal(dist, 0.0)
    dist = np.clip(dist, 0.0, None)
    dist = (dist + dist.T) / 2.0
    condensed = squareform(dist, checks=False)

    print(
        f"Complete-linkage clustering with MIN_SIM={MIN_SIM} "
        f"(both phrase & definition cos-sim must be >= {MIN_SIM})"
    )
    Z = linkage(condensed, method="complete")
    labels = fcluster(Z, t=DIST_THRESHOLD, criterion="distance")

    label_to_uuid: dict[int, str] = {}
    assignments: list[tuple[str, int]] = []
    for idx, row_id in enumerate(ids):
        lbl = int(labels[idx])
        if lbl not in label_to_uuid:
            label_to_uuid[lbl] = str(uuid.uuid4())
        assignments.append((label_to_uuid[lbl], row_id))

    cluster_sizes: dict[str, int] = {}
    for u, _ in assignments:
        cluster_sizes[u] = cluster_sizes.get(u, 0) + 1
    multi = sum(1 for s in cluster_sizes.values() if s > 1)
    singletons = sum(1 for s in cluster_sizes.values() if s == 1)
    largest = max(cluster_sizes.values())
    print(
        f"Clusters: {len(cluster_sizes)} total | "
        f"multi-row: {multi} | singletons: {singletons} | "
        f"largest: {largest}"
    )

    cur.executemany(
        "UPDATE phraseologisms SET similarity = ? WHERE id = ?",
        assignments,
    )
    conn.commit()
    conn.close()
    print(f"Done. Output DB: {DST_DB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
