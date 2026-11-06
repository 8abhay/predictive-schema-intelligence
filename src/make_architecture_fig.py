"""Conceptual architecture figure (not data-derived). Green = implemented in this study, amber = partial, grey = proposed only."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import config as C

boxes = [
    ("Schema metadata\ncollector", "proposed", 0.02, 0.62), ("Schema version\ncomparator", "impl", 0.27, 0.62),
    ("Lineage / dependency\nanalyzer", "proposed", 0.02, 0.18), ("Feature\nextraction", "impl", 0.27, 0.40),
    ("Risk prediction\nmodel", "impl", 0.52, 0.40), ("Risk score +\nexplanation", "partial", 0.74, 0.40),
    ("Alert / recommendation\nlayer", "proposed", 0.74, 0.08), ("CI / orchestrator hook\n(Airflow, dbt)", "proposed", 0.74, 0.74),
]
col = {"impl": "#cfe8cf", "partial": "#ffe9b3", "proposed": "#e2e2e2"}
fig, ax = plt.subplots(figsize=(8, 3.6)); ax.axis("off")
pos = {}
for name, kind, x, y in boxes:
    ax.add_patch(FancyBboxPatch((x, y), 0.20, 0.2, boxstyle="round,pad=0.01", fc=col[kind], ec="#555"))
    ax.text(x + 0.10, y + 0.10, name, ha="center", va="center", fontsize=7.5); pos[name] = (x, y)
def arrow(a, b):
    (x1, y1), (x2, y2) = pos[a], pos[b]
    ax.annotate("", xy=(x2, y2 + 0.10), xytext=(x1 + 0.21, y1 + 0.10), arrowprops=dict(arrowstyle="->", color="#444"))
arrow("Schema metadata\ncollector", "Schema version\ncomparator"); arrow("Schema version\ncomparator", "Feature\nextraction")
arrow("Lineage / dependency\nanalyzer", "Feature\nextraction"); arrow("Feature\nextraction", "Risk prediction\nmodel")
arrow("Risk prediction\nmodel", "Risk score +\nexplanation"); arrow("Risk score +\nexplanation", "Alert / recommendation\nlayer")
arrow("Alert / recommendation\nlayer", "CI / orchestrator hook\n(Airflow, dbt)")
for lab, k, x in [("Implemented (synthetic data)", "impl", 0.02), ("Partial", "partial", 0.30), ("Proposed only, not built", "proposed", 0.45)]:
    ax.add_patch(FancyBboxPatch((x, -0.05), 0.02, 0.05, boxstyle="round,pad=0.002", fc=col[k], ec="#555")); ax.text(x + 0.03, -0.025, lab, fontsize=7, va="center")
ax.set_xlim(0, 1); ax.set_ylim(-0.1, 1)
(C.RESULTS_DIR / "figures").mkdir(exist_ok=True)
fig.savefig(C.RESULTS_DIR / "figures" / "fig0_architecture.png", dpi=200, bbox_inches="tight")
print("architecture figure written")
