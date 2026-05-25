# Reproducible Machine Learning Research

Reproducibility is a fundamental principle of science. In machine learning, reproducibility means another researcher can run your code and obtain the same results. This is harder than it sounds due to randomness in training, environment dependencies, and underspecified experimental details.

## Sources of Non-Determinism

1. **Random initialization**: Weight initialization uses random seeds
2. **Data shuffling**: Training order affects optimization path
3. **Dropout and other stochastic layers**: Random masks during training
4. **Parallel computation**: Non-associative floating-point arithmetic in parallel GPU ops
5. **Library versions**: PyTorch 1.x vs 2.x may produce different results
6. **Hardware differences**: Different GPU architectures, precision modes

## Seeding for Reproducibility

```python
import random
import numpy as np
import torch

def set_seed(seed: int = 42):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    
    # For fully deterministic behavior (at cost of performance)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
    # PyTorch 2.0+ deterministic operations
    torch.use_deterministic_algorithms(True)

set_seed(42)
```

**Warning**: `torch.use_deterministic_algorithms(True)` can be ~30% slower and may raise errors for operations without deterministic implementations.

## Environment Pinning

```bash
# Export exact dependency versions
pip freeze > requirements.txt

# Preferred: use a lockfile manager
uv lock                  # uv
poetry lock              # poetry
pip-compile setup.cfg    # pip-tools
```

**Dockerfile for full environment capture**:
```dockerfile
FROM nvidia/cuda:12.1-devel-ubuntu22.04
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

## Experiment Tracking

Track hyperparameters, metrics, and artifacts for every experiment run:

```python
import mlflow

mlflow.set_experiment("bert-fine-tuning")

with mlflow.start_run(run_name="lr=5e-5_bs=32"):
    mlflow.log_params({
        "learning_rate": 5e-5,
        "batch_size": 32,
        "epochs": 3,
        "model": "bert-base-uncased",
    })
    
    for epoch in range(3):
        loss = train_epoch()
        acc = evaluate()
        mlflow.log_metrics({"loss": loss, "accuracy": acc}, step=epoch)
    
    mlflow.pytorch.log_model(model, "model")
    mlflow.log_artifact("confusion_matrix.png")
```

Alternatives: Weights & Biases (wandb), Neptune, ClearML.

## Data Versioning

```bash
# DVC: Git for data and models
dvc init
dvc add data/train.csv         # Track with DVC
git add data/train.csv.dvc     # Commit metadata to git
dvc push                        # Push data to remote storage (S3, GCS)

# Reproduce experiments
dvc repro                       # Re-run pipeline if inputs changed
```

## Checklist for Reproducible Papers

- [ ] Full code released (not just inference, but training scripts)
- [ ] Random seeds specified for all experiments
- [ ] Hardware specifications (GPU model, VRAM, CPU, memory)
- [ ] Training time reported
- [ ] All hyperparameters reported (including "obvious" ones like optimizer momentum)
- [ ] Dataset splits and preprocessing code released
- [ ] Multiple runs with different seeds; report mean ± std
- [ ] Statistical significance tests where relevant
- [ ] Model checkpoints hosted (HuggingFace Hub preferred)
- [ ] Docker image or conda environment provided

## Model Cards

Following Mitchell et al. (2019) model card framework:

```markdown
# Model Card: Sentiment Classifier

## Model Description
- Architecture: BERT-base fine-tuned on SST-2
- Training hardware: NVIDIA A100 80GB
- Training time: 45 minutes

## Training Data
- SST-2 (67,349 movie reviews)
- 80/10/10 train/val/test split

## Evaluation
| Metric | Value |
|--------|-------|
| Accuracy | 93.2% |
| F1 | 93.4% |

## Limitations
- Performance drops on domain-specific text (medical, legal)
- Tested only on English text
```

## The ML Reproducibility Crisis

Meta-analysis studies find that 60-70% of ML papers cannot be reproduced exactly, and many show significant performance gaps between claimed and reproduced results. Common causes:
- Undisclosed data filtering and cherry-picking
- Unreported hyperparameter search effort
- Test set contamination in pre-training data
