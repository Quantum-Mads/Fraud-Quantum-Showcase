"""One worked explanation: what the deployed tensor-train says about a single alert.

Scripts/03 measures how fast and how repeatable the exact attribution is; this
script records the attribution itself, for the highest-scoring fraud in the same
reduced 8-feature test sample, so the proposal can show what an analyst receives:
the exact contribution of every feature to that decision, and how far the score
sits from the tuned decision threshold.

The explained object is the SVD-compressed (bond dimension 8) tensor-train of the
same 300-tree XGBoost used in scripts/01 -- the model that would be deployed. Both
quantities are exact contractions, not samples: one masked pass per feature for the
attribution (qdistill.attribution) and one per neighbouring bin for the boundary
(qdistill.boundary_sensitivity).

Usage:
    uv run python scripts/16_explanation_example.py
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
from pathlib import Path

import numpy as np
import xgboost as xgb

from qdistill.attribution import exact_attribution, reference_from_training
from qdistill.boundary_sensitivity import boundary_sensitivity
from qdistill.config import RESULTS_TABLES_DIR
from qdistill.data import load_splits
from qdistill.metrics import best_f1_threshold
from qdistill.tree_to_tt import xgboost_to_tensor_train
from qdistill.tt_merge import svd_compress

_spec = importlib.util.spec_from_file_location("distill01", Path(__file__).parent / "01_distillation_compression.py")
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)
select_features, stratified_reduced_sample, XGB_PARAMS = (
    _m.select_features, _m.stratified_reduced_sample, _m.XGB_PARAMS)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--bond-dim", type=int, default=8)
    args = ap.parse_args()

    splits = load_splits("random")
    features = select_features(splits, args.seed)
    X_train, y_train = stratified_reduced_sample(splits.train, features, 60, 940, args.seed)
    X_val, y_val = stratified_reduced_sample(splits.val, features, 20, 380, args.seed + 1000)
    X_test, y_test = stratified_reduced_sample(splits.test, features, 20, 380, args.seed + 2000)

    n_pos, n_neg = y_train.sum(), len(y_train) - y_train.sum()
    model = xgb.XGBClassifier(**XGB_PARAMS, scale_pos_weight=n_neg / max(n_pos, 1), random_state=args.seed, n_jobs=-1)
    model.fit(X_train, y_train)
    cores, info = xgboost_to_tensor_train(model.get_booster(), features, base_score=0.5)
    compressed, _ = svd_compress(cores, max_bond=args.bond_dim)
    reference = reference_from_training(X_train, info)

    threshold = best_f1_threshold(y_val, model.predict_proba(X_val)[:, 1])
    logit_threshold = float(np.log(threshold / (1 - threshold)))

    # The alert an analyst would open: the highest-scoring transaction that is a real fraud.
    scores = model.predict_proba(X_test)[:, 1]
    fraud_rows = np.flatnonzero(y_test == 1)
    row = int(fraud_rows[np.argmax(scores[fraud_rows])])
    X_row = X_test[row: row + 1]

    attributions, logits = exact_attribution(compressed, info, X_row, reference)
    attr = attributions[0]
    logit = float(logits[0])
    log.info("explained row %d (true fraud), XGBoost probability %.4f, tensor-train logit %.3f (threshold %.3f)",
             row, scores[row], logit, logit_threshold)
    for f, a in sorted(zip(features, attr), key=lambda t: -abs(t[1])):
        log.info("  %-8s contributes %+.3f", f, a)

    # How close the same decision is to the threshold, on the same model.
    bs = boundary_sensitivity(compressed, info, X_row)
    moves = []
    for site, f in enumerate(features):
        for direction, delta, dist in (("left", -bs["left_delta"][0, site], bs["dist_to_left_edge"][0, site]),
                                       ("right", bs["right_delta"][0, site], bs["dist_to_right_edge"][0, site])):
            if not np.isnan(delta):
                moves.append({"feature": f, "direction": direction, "logit_change": float(delta),
                              "raw_distance_to_that_boundary": float(dist)})
    most_negative = min(moves, key=lambda m: m["logit_change"])
    margin = logit - logit_threshold
    log.info("margin above the threshold: %.3f logits; largest single-bin drop: %s %s (%.3f)",
             margin, most_negative["feature"], most_negative["direction"], most_negative["logit_change"])

    out = Path(RESULTS_TABLES_DIR) / "explanation_example.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "seed": args.seed, "bond_dim": args.bond_dim, "features": features,
        "explained_row": row, "true_label": int(y_test[row]),
        "xgboost_probability": float(scores[row]),
        "tensor_train_logit": logit,
        "decision_threshold_logit": logit_threshold,
        "margin_above_threshold_logit": float(margin),
        "attributions": {f: float(a) for f, a in zip(features, attr)},
        "largest_single_bin_drop": most_negative,
        "single_bin_move_would_flip_prediction": bool(logit + most_negative["logit_change"] < logit_threshold),
    }, indent=2))
    log.info("Wrote %s", out)


if __name__ == "__main__":
    main()
