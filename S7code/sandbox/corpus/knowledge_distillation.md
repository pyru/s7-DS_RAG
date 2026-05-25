# Knowledge Distillation: Compressing Neural Networks

Knowledge distillation (Hinton et al., 2015) transfers knowledge from a large, expensive "teacher" model to a compact "student" model. The student learns not just from ground-truth labels but from the teacher's output distributions — the "dark knowledge" embedded in how the teacher distributes probability across wrong answers.

## Why Soft Labels?

Hard labels (one-hot vectors) discard structure: cat=1, dog=0, car=0 treats dog and car as equally wrong. Soft labels from a teacher preserve relationships: cat=0.85, dog=0.12, car=0.03 reveals that cat-like things are similar to dogs.

A student trained on soft labels generalizes better: the probability mass distribution encodes which classes are confused and how, providing much richer training signal per example.

## Standard Distillation Loss

```
L = α · L_CE(y_hard, q_student) + (1-α) · T² · L_KL(p_teacher, q_student)
```

Where:
- T is the temperature (smooths distributions; higher T → softer, more informative labels)
- α balances hard and soft label losses
- T² compensates for gradient magnitude scaling by temperature

At T=1: normal softmax probabilities. At T=5–10: near-uniform distributions that expose inter-class relationships.

## Feature-Level Distillation

Beyond output distributions, students can learn from intermediate representations:

**Attention transfer** (Zagoruyko & Komodakis, 2017): Student matches teacher's spatial attention maps, encoded as L2-normalized feature activation magnitudes.

**FitNets**: Student is trained to match the feature maps of a specific teacher layer through a learned regressor (hint training).

**Relational knowledge distillation**: Match pairwise or triplet distances between examples in feature space.

## Self-Distillation

A model can distill knowledge from itself:
- Born-again networks: train a copy of the same architecture on the original's outputs — it generalizes better despite identical capacity
- Snapshot ensembles: distill multiple checkpoints saved during training

## Applications

**DistilBERT**: Distilled BERT (66M vs 110M parameters) retains 97% of BERT performance at 60% speed. Uses:
- Token-level loss on teacher's softmax
- Cosine embedding loss matching hidden states
- Standard masked language modeling loss

**TinyBERT**: More aggressive compression (14.5M vs 110M params) matching both attention matrices and hidden states at multiple layers.

**GPT distillation**: Challenging due to auto-regressive generation; common approach is sequence-level distillation using teacher samples as training data.

## Quantization vs Distillation

Quantization (int8, int4) reduces precision of weights and activations. Distillation reduces model size structurally. Combined: quantize a distilled model for maximum compression.

## Evaluation: Student-Teacher Gap

Measure the student-teacher gap on held-out benchmarks:
- Student at 50% parameters: typical 2-4% accuracy drop on GLUE
- Student at 10% parameters: typical 5-10% accuracy drop
- With feature distillation: recover ~half the student-teacher gap vs output-only distillation
