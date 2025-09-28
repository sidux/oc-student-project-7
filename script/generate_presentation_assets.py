#!/usr/bin/env python3
import re
from pathlib import Path
import json

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "result" / "reports"
PLOTS = ROOT / "result" / "plots"
PLOTS.mkdir(parents=True, exist_ok=True)


def parse_report(path: Path):
    acc = None
    macro_f1 = None
    macro_p = None
    macro_r = None
    text = path.read_text()
    # accuracy line
    m_acc = re.search(r"^\s*accuracy\s+([0-9.]+)", text, flags=re.M)
    if m_acc:
        acc = float(m_acc.group(1))
    # macro avg line: precision, recall, f1-score
    m_macro = re.search(r"^\s*macro avg\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)", text, flags=re.M)
    if m_macro:
        macro_p = float(m_macro.group(1))
        macro_r = float(m_macro.group(2))
        macro_f1 = float(m_macro.group(3))
    return acc, macro_p, macro_r, macro_f1


def main():
    files = {
        "LogReg (lemma)": REPORTS / "logreg_cr_lemma.txt",
        "LogReg (stem)": REPORTS / "logreg_cr_stem.txt",
        "LSTM rnd (lemma)": REPORTS / "lstm_cr_lemma_random.txt",
        "LSTM rnd (stem)": REPORTS / "lstm_cr_stem_random.txt",
        "LSTM GloVe (lemma)": REPORTS / "lstm_cr_glove_lemma.txt",
        "LSTM GloVe (stem)": REPORTS / "lstm_cr_glove_stem.txt",
        "LSTM W2V (lemma)": REPORTS / "lstm_cr_w2v_lemma.txt",
        "LSTM W2V (stem)": REPORTS / "lstm_cr_w2v_stem.txt",
        "BERT (lemma)": REPORTS / "bert_cr_lemma.txt",
        "BERT (stem)": REPORTS / "bert_cr_stem.txt",
    }

    entries = []
    for name, path in files.items():
        if path.exists():
            acc, mp, mr, mf1 = parse_report(path)
            entries.append({
                "name": name,
                "accuracy": acc,
                "macro_precision": mp,
                "macro_recall": mr,
                "macro_f1": mf1,
            })

    # Save json for reproducibility
    (PLOTS / "summary_metrics.json").write_text(json.dumps(entries, indent=2))

    # Accuracy bar chart
    labels = [e["name"] for e in entries]
    accs = [e["accuracy"] for e in entries]
    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.bar(labels, accs, color="#3498db")
    ax.set_title("Accuracy par modèle (test)")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0.7, max(accs) + 0.05)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    for b, v in zip(bars, accs):
        ax.text(b.get_x() + b.get_width()/2, b.get_height()+0.005, f"{v:.3f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(PLOTS / "summary_accuracy.png", dpi=200)

    # Macro F1 bar chart
    f1s = [e["macro_f1"] for e in entries]
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    bars2 = ax2.bar(labels, f1s, color="#2ecc71")
    ax2.set_title("Macro F1 par modèle (test)")
    ax2.set_ylabel("Macro F1")
    ax2.set_ylim(0.7, max(f1s) + 0.05)
    ax2.set_xticklabels(labels, rotation=35, ha="right")
    for b, v in zip(bars2, f1s):
        ax2.text(b.get_x() + b.get_width()/2, b.get_height()+0.005, f"{v:.3f}", ha="center", va="bottom", fontsize=9)
    fig2.tight_layout()
    fig2.savefig(PLOTS / "summary_macro_f1.png", dpi=200)

    print("Assets written:")
    print(PLOTS / "summary_accuracy.png")
    print(PLOTS / "summary_macro_f1.png")


if __name__ == "__main__":
    main()

