# LLM Scaling Laws: Predicting Model Performance

Scaling laws describe how language model performance improves predictably as a function of model size, dataset size, and compute budget. Understanding scaling laws guides efficient resource allocation and sets expectations for future capabilities.

## Kaplan Scaling Laws (OpenAI, 2020)

Kaplan et al. found that language model loss follows power laws with model parameters N, dataset tokens D, and compute C:

```
L(N) ≈ (Nₓ/N)^αₙ    [model-size scaling]
L(D) ≈ (Dₓ/D)^αₐ    [data scaling]
L(C) ≈ (Cₓ/C)^αₓ    [compute scaling]
```

Where α values are empirically measured (~0.076 for parameters, ~0.095 for data).

**Key findings**:
1. Performance follows smooth power laws over 7 orders of magnitude in compute
2. For a fixed compute budget, it is better to train a larger model on less data than a smaller model on more data
3. Large models are more sample-efficient than small models

## Chinchilla Scaling Laws (DeepMind, 2022)

Hoffmann et al. challenged Kaplan's recommendation. Using more careful analysis:

**Optimal allocation**: For a fixed compute budget C = 6ND (rough token cost estimate), optimal training requires:
```
N_opt = (C / 6)^0.5 · (αₙ/αₐ)^(αₙ/(αₙ+αₐ))
D_opt = (C / 6)^0.5 · (αₐ/αₙ)^(αₙ/(αₙ+αₐ))
```

Simplified rule: **Train on ~20 tokens per parameter** for compute-optimal training.

**Implication**: GPT-3 (175B params, 300B tokens) was severely undertrained. A 70B model trained on 1.4T tokens (LLaMA 2 70B) outperforms it despite using similar total compute.

## Emergent Abilities

Some capabilities appear suddenly at certain scales rather than improving smoothly:

- Multi-step arithmetic: appears ~62B parameters
- Chain-of-thought reasoning: appears ~100B parameters  
- Instruction following (zero-shot): appears ~100B+ parameters

This "emergence" may be an artifact of discrete metrics — continuous metrics show smoother scaling.

## Data Scaling Challenges

The Chinchilla laws assume data quality. In practice:
- Web text quality degrades as dataset size grows (more spam, low-quality content)
- Repeating data hurts performance (diminishing returns at 4+ epochs)
- High-quality curated data (textbooks, academic papers, code) is far more valuable per token

**LLaMA 3** estimates that high-quality data is worth ~10× lower-quality web text in tokens.

## Inference Compute Scaling

**Test-time compute** (inference-time compute): Spending more compute at inference time can significantly boost performance:
- Chain-of-thought prompting
- Self-consistency (majority vote over multiple samples)
- Tree-of-thought search
- Process reward models guiding step-by-step solutions

OpenAI's o1 model demonstrated that scaling inference compute can match or exceed scaling training compute for reasoning tasks.

## Implications for Practitioners

1. **Don't train small models to convergence**: If you have more data, use it on a proportionally larger model
2. **Estimate needed compute before training**: Use scaling laws to predict target loss and required compute
3. **Data quality dominates at large scale**: Invest in data curation, deduplication, and filtering
4. **Downstream task performance can diverge from perplexity**: Always evaluate on target tasks
5. **Continued pre-training beats domain-specific pretraining**: Start from a large base model, then domain-adapt

## Beyond Language Models

Scaling laws extend to other domains with appropriate modifications:
- **Code**: Similar power laws but steeper — code models benefit more from scale
- **Vision**: Similar laws observed for image classification and generation
- **Multimodal**: Still being studied; generally follows language model laws with vision adjustment
