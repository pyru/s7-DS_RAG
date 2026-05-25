# Fine-tuning Large Language Models

Fine-tuning adapts a pre-trained LLM to a specific domain or task by training on curated data. With parameter-efficient methods like LoRA, fine-tuning frontier-class models on consumer hardware has become practical.

## Full Fine-tuning

Full fine-tuning updates all model parameters. It produces the best results but requires:
- GPU memory for model parameters + gradients + optimizer states
- For LLaMA 7B: ~112 GB GPU memory with Adam optimizer (FP32 optimizer states)
- Practical only on multi-GPU setups or with DeepSpeed/FSDP parallelism

## Instruction Fine-tuning

Instruction tuning (Wei et al., 2021) teaches models to follow natural language instructions. Training data consists of (instruction, response) pairs:

```json
{
  "instruction": "Translate the following to French.",
  "input": "The weather is beautiful today.",
  "output": "Le temps est magnifique aujourd'hui."
}
```

Public datasets: Alpaca (52K GPT-4 generated examples), Dolly (15K human-written), FLAN collection (1800+ tasks).

## LoRA: Low-Rank Adaptation

LoRA (Hu et al., 2021) freezes pre-trained weights and adds trainable low-rank decomposition matrices to each attention layer:

```
W = W_pretrained + BA
```

Where B ∈ ℝ^(d×r) and A ∈ ℝ^(r×k), with rank r ≪ min(d,k). Typical rank: 4–64.

Benefits:
- 10,000× fewer trainable parameters than full fine-tuning
- Adapter matrices stored separately — switch tasks by swapping adapters
- Merge with base model at inference: `W = W_pretrained + scale * BA` → zero inference overhead

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], 
                    lora_dropout=0.05, bias="none")
model = get_peft_model(base_model, config)
model.print_trainable_parameters()  # "trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.06"
```

## QLoRA: Quantized LoRA

QLoRA (Dettmers et al., 2023) enables fine-tuning 65B models on a single 48GB GPU:
1. Quantize base model to 4-bit NormalFloat (NF4)
2. Train LoRA adapters in BFloat16
3. Use paged optimizer states to handle memory spikes

This made fine-tuning state-of-the-art models accessible to individuals.

## Reinforcement Learning from Human Feedback (RLHF)

RLHF (used in InstructGPT, Claude, Gemini) aligns models with human preferences:

1. **SFT**: Supervised fine-tuning on human demonstrations
2. **Reward Model**: Train a reward model on human preference rankings (A preferred over B)
3. **PPO**: Use proximal policy optimization to maximize expected reward, with KL penalty to prevent drift from SFT model

```python
# PPO objective (simplified)
L = E[min(r(θ)·A, clip(r(θ), 1-ε, 1+ε)·A)] - β·KL[π_θ || π_ref]
```

## DPO: Direct Preference Optimization

DPO (Rafailov et al., 2023) achieves RLHF-equivalent results without explicit reward modeling. It directly optimizes the policy using preference pairs:

```
L_DPO = -E[log σ(β log(π_θ(y_w)/π_ref(y_w)) - β log(π_θ(y_l)/π_ref(y_l)))]
```

DPO is simpler, more stable, and increasingly preferred over PPO in practice.

## Evaluation

Fine-tuned models should be evaluated on:
- **Task-specific benchmarks**: accuracy on target tasks
- **Catastrophic forgetting**: performance retained on general capabilities
- **Alignment**: refusal rate on harmful queries, honesty on uncertain knowledge
