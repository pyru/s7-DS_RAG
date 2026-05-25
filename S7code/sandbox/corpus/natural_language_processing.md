# Natural Language Processing: Core Concepts and Techniques

Natural Language Processing (NLP) is the intersection of computational linguistics and machine learning that enables computers to understand, interpret, and generate human language. Modern NLP is dominated by large transformer-based language models, but understanding classical foundations remains essential.

## Text Preprocessing Pipeline

### Tokenization

Tokenization splits text into minimal processing units:

**Word tokenization**: Simple but struggles with contractions ("don't"), compounds, and non-space-delimited languages.

**Subword tokenization** (modern standard):
- **BPE (Byte Pair Encoding)**: Merges frequent character pairs iteratively. Used in GPT-series.
- **WordPiece**: Similar to BPE but uses likelihood rather than frequency. Used in BERT.
- **SentencePiece**: Language-independent; treats text as a byte sequence. Used in LLaMA.

Vocabulary sizes typically range from 32K to 100K tokens.

### Text Normalization

- **Lowercasing**: "Apple" → "apple" (avoid for named entity tasks)
- **Stopword removal**: Remove function words for bag-of-words tasks
- **Lemmatization**: "running" → "run", "better" → "good" (dictionary lookup)
- **Stemming**: "running" → "run" (rule-based, faster but cruder)

## Classical NLP Tasks

### Named Entity Recognition (NER)

Identify and classify named entities in text:
```
"Barack Obama was born in Honolulu, Hawaii."
 [PER: Barack Obama]               [LOC: Honolulu] [LOC: Hawaii]
```

Models: BiLSTM-CRF (classical), BERT-based (current standard), LLM prompting (few-shot).

### Dependency Parsing

Identify grammatical relationships between words:
```
"The cat chased the mouse."
chased → cat (nsubj)
chased → mouse (dobj)
cat → The (det)
mouse → the (det)
```

spaCy provides fast, accurate dependency parsing.

### Coreference Resolution

Determine which mentions refer to the same entity:
```
"Alice told Bob that she would help him."
she = Alice, him = Bob
```

Challenging due to world knowledge requirements and context dependence.

## Sequence-to-Sequence Tasks

### Machine Translation

Encoder-decoder models map source language sequences to target:
- Classical: Moses (phrase-based statistical MT)
- Neural: seq2seq with attention (Luong, Bahdanau)
- Modern: transformer-based (MarianMT, NLLB-200, GPT-4)

### Summarization

- **Extractive**: Select important sentences from source document (TextRank)
- **Abstractive**: Generate new sentences capturing key content (BART, T5, GPT)

### Question Answering

- **Extractive QA**: Extract answer span from given context (BERT + linear head on SQuAD)
- **Generative QA**: Generate free-form answers (GPT, Flan-T5)
- **Open-domain QA**: Retrieve relevant documents, then extract/generate answer (RAG)

## Word Representations

**One-hot encoding**: Sparse; no semantic similarity; O(V) dimensions

**Word2Vec** (Mikolov et al., 2013): Dense 300-dim embeddings from co-occurrence patterns
- Skip-gram: Predict context from center word
- CBOW: Predict center from context
- Captures analogy: king - man + woman ≈ queen

**GloVe**: Global Vectors; factorizes co-occurrence matrix. Similar quality to Word2Vec.

**FastText**: Character n-gram embeddings; handles morphological variation and OOV words.

**Contextual embeddings** (ELMo, BERT): Same word gets different vectors in different contexts.

## Sentiment Analysis

```python
# Simple rule-based (VADER)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
scores = sia.polarity_scores("I absolutely love this product!")
# {'neg': 0.0, 'neu': 0.2, 'pos': 0.8, 'compound': 0.8516}

# Neural (fine-tuned BERT)
from transformers import pipeline
classifier = pipeline("sentiment-analysis")
result = classifier("This movie was fantastic!")
# [{'label': 'POSITIVE', 'score': 0.9998}]
```
