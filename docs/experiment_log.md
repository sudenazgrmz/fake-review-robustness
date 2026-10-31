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
