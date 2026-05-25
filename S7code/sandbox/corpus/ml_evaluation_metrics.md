# Machine Learning Evaluation Metrics

Selecting appropriate evaluation metrics is as important as model selection. The right metric depends on the task, class balance, and business context.

## Classification Metrics

### Confusion Matrix Terms

For binary classification:
- **TP (True Positive)**: Correctly predicted positive
- **TN (True Negative)**: Correctly predicted negative
- **FP (False Positive)**: Negative incorrectly predicted as positive (Type I error)
- **FN (False Negative)**: Positive incorrectly predicted as negative (Type II error)

### Accuracy

```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

**Problem**: Misleading on imbalanced datasets. A model predicting "negative" always achieves 99% accuracy when 99% of samples are negative.

### Precision, Recall, F1

```
Precision = TP / (TP + FP)   # Of predicted positives, how many are actually positive?
Recall    = TP / (TP + FN)   # Of actual positives, how many did we catch?
F1        = 2 · (P · R) / (P + R)   # Harmonic mean of precision and recall
```

**When to prefer precision**: Spam detection (FP = legitimate email in spam folder)
**When to prefer recall**: Disease screening (FN = missed diagnosis)
**Fβ**: Fβ = (1+β²)·P·R / (β²·P + R) — use β>1 to weight recall, β<1 to weight precision

### AUC-ROC

The ROC curve plots TPR (recall) vs FPR (fall-out) at all classification thresholds. AUC (Area Under Curve) equals the probability that a randomly chosen positive example ranks above a randomly chosen negative example.

- AUC = 1.0: perfect classifier
- AUC = 0.5: no better than random
- AUC = 0.0: always wrong (flip predictions for perfect model)

AUC is threshold-independent and robust to class imbalance.

### Matthews Correlation Coefficient (MCC)

MCC is arguably the best single metric for binary classification:
```
MCC = (TP·TN - FP·FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN))
```
Range: [-1, +1]. Unlike F1, it accounts for all four confusion matrix cells.

## Regression Metrics

```
MAE  = mean(|y - ŷ|)          # Mean Absolute Error — robust to outliers
MSE  = mean((y - ŷ)²)         # Mean Squared Error — penalizes large errors
RMSE = √MSE                    # Interpretable in same units as target
R²   = 1 - SS_res/SS_tot      # Coefficient of determination; 1.0 = perfect
```

## NLP Metrics

### BLEU (Bilingual Evaluation Understudy)

BLEU measures n-gram overlap between generated text and reference:
```
BLEU = BP · exp(∑ wₙ log pₙ)
```
Where BP is brevity penalty (penalizes short generations) and pₙ is modified precision for n-grams.

**Limitations**: Can be gamed with repetitive text; poor correlation with human judgment for diverse generation tasks.

### ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

ROUGE measures recall of n-grams in reference text appearing in the generated text. ROUGE-L uses longest common subsequence.

Commonly used for summarization evaluation.

### BERTScore

BERTScore uses BERT embeddings to measure semantic similarity between generated and reference text. Better correlation with human judgment than BLEU/ROUGE.

### Perplexity

Perplexity measures how well a language model predicts a text sample:
```
PPL = exp(-1/N · ∑ log p(wᵢ|w₁...wᵢ₋₁))
```
Lower perplexity = better language model. Not directly comparable across different tokenizations or vocabularies.

## Retrieval Metrics

- **Recall@k**: Fraction of relevant documents in top-k results
- **Precision@k**: Fraction of top-k results that are relevant
- **MRR (Mean Reciprocal Rank)**: Average of 1/rank of first relevant result
- **NDCG (Normalized Discounted Cumulative Gain)**: Accounts for position and graded relevance
