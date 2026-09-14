"""Regenerates Figure 2 of the proposal from the committed JSON tables, without
re-running any experiment: (a) the compression curve
(results/tables/distillation_compression.json), (b) compiled latency
(results/tables/latency_compiled.json) and (c) the worked explanation of one alert
(results/tables/explanation_example.json).

Usage:
    uv run python scripts/make_figures.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TABLES = Path("results/tables")
OUT = Path("figures")


def load(name: str) -> dict | None:
    p = TABLES / name
    return json.loads(p.read_text()) if p.exists() else None


def main() -> None:
    OUT.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2), constrained_layout=True)

    comp = load("distillation_compression.json")
    ax = axes[0]
    if comp:
        caps = sorted(int(c) for c in comp["compression_curve"])
        auprc = [comp["compression_curve"][str(c)]["test"]["auprc"] for c in caps]
        ax.axhline(comp["xgboost_test"]["auprc"], color="gray", ls="--", lw=1, label="XGBoost (exact)")
        ax.plot(caps, auprc, "o-", color="#2ca02c", ms=4, label="Compressed tensor-train")
        ax.set_xscale("log", base=2); ax.set_xticks(caps); ax.set_xticklabels([str(c) for c in caps])
        lo = min(auprc + [comp["xgboost_test"]["auprc"]]); ax.set_ylim(lo - 0.006, lo + 0.014)
    ax.set_xlabel("Bond dimension"); ax.set_ylabel("Test AUPRC"); ax.set_title("(a) Compression curve")
    ax.legend(frameon=False, fontsize=7, loc="lower right")

    lat = load("latency_compiled.json")
    ax = axes[1]
    if lat:
        agg = lat["aggregated"]
        batch = sorted(int(b) for b in agg)
        for key, label, color, marker in (("xgboost", "XGBoost", "#1f77b4", "o"),
                                          ("xgboost_onnx", "XGBoost (ONNX Runtime)", "#17becf", "D"),
                                          ("tt_numba", "Tensor-train (Numba)", "#2ca02c", "s")):
            m = [agg[str(b)][key]["mean"] for b in batch]; s = [agg[str(b)][key]["std"] for b in batch]
            ax.errorbar(batch, m, yerr=s, fmt=marker + "-", color=color, ms=4, capsize=2, label=label)
        ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Batch size"); ax.set_ylabel("Inference time (ms)")
    ax.set_title(f"(b) Latency, compiled ({lat['n_seeds'] if lat else '?'} runs)"); ax.legend(frameon=False, fontsize=7)

    # one worked explanation from the deployed (compressed) network: each bar is the score lost if that
    # feature were unknown, an exact masked contraction (occlusion values, so they need not sum to the score)
    ex = load("explanation_example.json")
    ax = axes[2]
    if ex:
        attr = sorted(ex["attributions"].items(), key=lambda kv: abs(kv[1]))
        names = [k for k, _ in attr]; vals = [v for _, v in attr]
        ax.barh(range(len(names)), vals, color=["#d62728" if v > 0 else "#1f77b4" for v in vals], height=0.62)
        ax.axvline(0, color="black", lw=0.6)
        ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=7)
        span = max(abs(v) for v in vals)
        for i, v in enumerate(vals):
            ax.text(v + (0.04 * span if v >= 0 else -0.04 * span), i, f"{v:+.2f}",
                    va="center", ha="left" if v >= 0 else "right", fontsize=6)
        lo, hi = min(min(vals), 0.0), max(vals)
        ax.set_xlim(lo - 0.30 * span, hi + 0.42 * span)
    ax.set_xlabel("Score lost if unknown (logits)")
    ax.set_title("(c) Why this alert fired")

    fig.savefig(OUT / "results.png", dpi=200)
    print("wrote", OUT / "results.png")


if __name__ == "__main__":
    main()
