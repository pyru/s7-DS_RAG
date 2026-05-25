# GPT Model Evolution: From GPT-1 to Modern LLMs

The GPT (Generative Pre-trained Transformer) family, developed by OpenAI, represents the most influential line of decoder-only language models. Each iteration demonstrated that scale and data quality could unlock qualitatively new capabilities.

## GPT-1 (2018): The Transfer Learning Hypothesis

GPT-1 (Radford et al., 2018) was a 117M parameter decoder-only transformer trained on BooksCorpus (800M words) using unsupervised language modeling (next-token prediction). The key insight was that this unsupervised pre-training could learn useful language representations for diverse downstream tasks with minimal fine-tuning.

GPT-1 achieved competitive performance on NLI, commonsense reasoning, and QA benchmarks, validating the transfer learning hypothesis for language.

## GPT-2 (2019): Zero-Shot Generalization

GPT-2 (1.5B parameters) was trained on WebText, 8 million web pages curated from Reddit with ≥3 karma. Its headline finding: **language models can perform tasks without any task-specific training** when framed correctly as language modeling problems.

"Translate English to French: 'cheese' → " → model outputs "fromage"

OpenAI famously delayed GPT-2's full release citing misuse concerns, which itself generated significant publicity. The 1.5B version was eventually released in November 2019.

## GPT-3 (2020): In-Context Learning at Scale

GPT-3's 175B parameters enabled a qualitative leap: **in-context learning** from examples provided in the prompt without gradient updates. With few-shot prompting, GPT-3 matched fine-tuned BERT on many benchmarks.

Key findings from the GPT-3 paper:
- Few-shot performance scales predictably with model size
- Model acquires task understanding purely from examples in context
- Meta-learning emerges at sufficient scale

The API-based access model demonstrated that capable AI could be delivered as a service, spawning the modern AI product ecosystem.

## InstructGPT / RLHF (2022)

Raw language models optimize next-token prediction, not helpfulness. InstructGPT applied **Reinforcement Learning from Human Feedback (RLHF)**:
1. Fine-tune GPT-3 on human-written demonstrations of desired behavior
2. Train a reward model to predict human preference rankings
3. Use PPO (Proximal Policy Optimization) to optimize the LM against the reward model

This alignment technique made models dramatically more helpful, harmless, and honest — enabling safe deployment as ChatGPT.

## GPT-4 (2023): Multimodal and Reasoning

GPT-4 added image understanding (GPT-4V) and achieved near-human performance on numerous professional exams (bar exam, SAT, AP exams). The technical report released minimal architectural details.

Key advances:
- System prompts for customizable behavior
- Longer context window (8K→128K tokens)
- Image input processing
- Improved instruction following and reduced hallucination

## Open-Source Alternatives

The release of Meta's **LLaMA** (2023) democratized access to capable base models:
- **LLaMA 2**: 7B–70B parameters, commercially licensed
- **LLaMA 3**: Competitive with GPT-4-class models at 70B+ parameters
- **Mistral 7B**: Outperforms LLaMA 2 13B with grouped-query attention and sliding window attention

**Gemini** (Google DeepMind) and **Claude** (Anthropic) offer competing frontier capabilities.

## Scaling Laws

Chinchilla scaling laws (Hoffmann et al., 2022) showed that most LLMs were undertrained relative to their parameter count. The optimal compute allocation trains a model with ~20 tokens per parameter: a 70B model should train on ~1.4T tokens.
