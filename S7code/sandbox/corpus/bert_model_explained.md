# BERT: Bidirectional Encoder Representations from Transformers

BERT (Devlin et al., 2018) was the first large-scale pre-trained model to achieve state-of-the-art performance across a wide range of NLP tasks using a single fine-tuning approach. It demonstrated that unsupervised pre-training on massive text corpora followed by supervised fine-tuning could dramatically outperform task-specific architectures.

## Key Innovation: Bidirectional Pre-training

Before BERT, language models were unidirectional — they predicted the next word given previous words (GPT, ELMo forward pass) or processed text as two separate unidirectional models concatenated. BERT is trained bidirectionally: each token attends to all other tokens in both directions simultaneously.

This bidirectional context enables BERT to build richer representations. "The bank can guarantee deposits" — here "bank" has different meanings depending on surrounding words in both directions.

## Pre-training Objectives

BERT uses two pre-training tasks:

### Masked Language Modeling (MLM)
15% of input tokens are randomly masked. The model predicts the masked tokens using bidirectional context:

```
Input:  "The [MASK] sat on the mat."
Target: "The cat sat on the mat."
```

Specifically, of the 15% selected tokens:
- 80% replaced with [MASK]
- 10% replaced with a random token
- 10% left unchanged (forces model to keep original tokens in representations)

### Next Sentence Prediction (NSP)
Given two sentences A and B, predict if B is the actual next sentence after A (50% true pairs, 50% random). This teaches inter-sentence relationships. (Later research showed NSP is less useful than MLM.)

## Architecture

BERT-Base: 12 transformer encoder layers, 768 hidden dimensions, 12 attention heads, 110M parameters
BERT-Large: 24 layers, 1024 dimensions, 16 heads, 340M parameters

Special tokens:
- `[CLS]`: prepended to every sequence; its final representation is used for classification
- `[SEP]`: separates sentence pairs
- `[MASK]`: placeholder for masked tokens during pre-training

## Fine-tuning

BERT's architecture supports diverse downstream tasks with minimal modification:

- **Classification**: single linear layer on `[CLS]` representation
- **NER/Tagging**: linear layer on each token representation
- **QA (SQuAD)**: two linear layers predicting start and end positions of answer span
- **Sentence similarity**: `[CLS]` of concatenated sentence pair through classifier

Fine-tuning typically requires only 2–4 epochs on task-specific data with learning rates of 2e-5 to 5e-5.

## Variants and Successors

- **RoBERTa** (2019): Removes NSP, trains longer with more data and larger batches — consistently outperforms BERT
- **DistilBERT**: Knowledge-distilled BERT, 40% smaller, 60% faster, retains 97% of performance
- **ALBERT**: Parameter sharing across layers, factorized embedding matrices — reduces parameters 18×
- **DeBERTa**: Disentangled attention separates content and position encodings — achieves SOTA on SuperGLUE

## Impact

BERT democratized transfer learning in NLP. It established that:
1. Massive unsupervised pre-training can capture linguistic knowledge
2. Minimal task-specific architecture is sufficient for most NLP tasks
3. Bidirectional context significantly outperforms unidirectional modeling for understanding tasks

The pre-train-then-fine-tune paradigm pioneered by BERT now dominates NLP, computer vision, and multimodal learning.
