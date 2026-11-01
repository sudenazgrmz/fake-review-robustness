# Experiment Log

## 2026-10-31 - TF-IDF baselines on OpSpam v1.4

- Data: deceptive-opinion.csv, 1600 reviews, balanced (800 truthful, 800 deceptive)
- Input: text only (source and hotel columns NOT given to the model)
- Splits: stratified 5-fold (random_state=42) and GroupKFold by hotel (5 folds)
- Metric: macro-F1

| Model | Random split | Grouped split |
| --- | --- | --- |
| TF-IDF + LogReg | 0.885 +/- 0.014 | 0.870 +/- 0.015 |
| TF-IDF + LinearSVC | 0.896 +/- 0.008 | 0.884 +/- 0.018 |

Notes:
- Gap between splits is about one std, so hotel memorization is not a major problem here (not conclusive with 5 folds).
- Top features: truthful -> concrete details (floor, bathroom, small, street); deceptive -> personal narrative (my stay, husband, vacation) and generic praise (luxury, definitely).
- Possible shortcuts: "priceline" (source artifact), place names (chicago, hilton, millennium).
- Limitation: all deceptive reviews come from one source (Mechanical Turk).

## 2026-10-31 - Ablation: removing suspected shortcut words

- Setup: same models, GroupKFold by hotel (5 folds), macro-F1.
- Removed (case-insensitive, whole words): source names (priceline, expedia, orbitz, tripadvisor, yelp; 55 reviews affected) and place/hotel names (chicago, michigan, hilton, millennium + all 20 hotel names; 1268 reviews affected).

| Model | baseline | no source names | no place/hotel names | both removed |
| --- | --- | --- | --- | --- |
| LogReg | 0.870 | 0.869 | 0.862 | 0.860 |
| SVM | 0.884 | 0.882 | 0.871 | 0.870 |

Notes:
- Drops are small (<= 0.014) and within about one std; same direction in both models.
- Source names rarely appear (55 reviews), so they cannot move the score much despite high coefficients.
- Place/hotel names may contribute about one point of macro-F1.
- Not tested: whether the model learns "Mechanical Turk style vs web style" instead of deception. Needs a deceptive set from another source.

## 2026-11-01 - TF-IDF vs DistilBERT, GroupKFold by hotel (5 folds)

- Same 5 folds for all models. DistilBERT (distilbert-base-uncased): max_len 256, batch 16, 3 epochs, lr 2e-5, AdamW wd 0.01, seed 42 (single seed). Input: text only.
- Files: results_5fold.csv, predictions_5fold.csv

| Model | macro-F1 | false positive rate (truthful flagged deceptive) |
| --- | --- | --- |
| TF-IDF + LogReg | 0.870 +/- 0.017 | 0.108 +/- 0.016 |
| TF-IDF + LinearSVC | 0.884 +/- 0.021 | 0.095 +/- 0.029 |
| DistilBERT | 0.885 +/- 0.017 | 0.152 +/- 0.044 |

Notes:
- DistilBERT vs SVM: mean diff +0.001, per-fold diffs change sign (+0.002, -0.022, +0.021, -0.019, +0.022). No evidence of a difference.
- DistilBERT vs LogReg: >= 0 in all 5 folds, mean +0.015. Suggestive, not conclusive (5 correlated folds).
- DistilBERT flags more truthful reviews as deceptive (15% vs ~10%).
- Limits: single seed, no hyperparameter tuning, 256-token truncation, all deceptive reviews from one source (MTurk).
- H1 not supported vs SVM; weakly suggested vs LogReg.
