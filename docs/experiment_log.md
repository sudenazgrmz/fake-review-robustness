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
