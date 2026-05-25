# Corpus Index: Agent7 S7 Knowledge Base

This document provides an overview of all 55+ documents in the Agent7 corpus, organized by topic.

## Group 1: Information Theory and Claude Shannon
1. `claude_shannon_information_theory.md` — Shannon's biography, entropy, channel capacity, information theory fundamentals
2. `information_theory_basics.md` — Entropy, KL divergence, mutual information, cross-entropy, data compression theorem
3. `data_compression_coding.md` — Huffman coding, LZ77, DEFLATE, Zstandard, neural compressors

## Group 2: Tokyo and Japan
4. `tokyo_activities_guide.md` — Tokyo sightseeing, cultural sites, food, day trips
5. `tokyo_weather_patterns.md` — Seasonal weather, cherry blossom timing, typhoon season, packing guide
6. `tokyo_neighborhoods.md` — Shinjuku, Shibuya, Asakusa, Akihabara, Roppongi district guides
7. `tokyo_transportation.md` — Suica card, Yamanote Line, subway system, airport access
8. `japan_culture_etiquette.md` — Customs, greetings, food manners, temple etiquette

## Group 3: Python and Asyncio
9. `python_asyncio_fundamentals.md` — Event loop, coroutines, gather, Tasks, asyncio.run()
10. `asyncio_advanced_patterns.md` — TaskGroup, queues, timeouts, async generators, semaphores
11. `python_concurrency.md` — GIL, threading, multiprocessing, subprocess, concurrency vs parallelism
12. `python_generators_iterators.md` — Yield, generator expressions, yield from, infinite sequences
13. `python_type_hints.md` — Type annotations, generics, Protocol, TypedDict, mypy
14. `pydantic_guide.md` — BaseModel, validation, nested models, settings, JSON schema
15. `python_testing_guide.md` — pytest, fixtures, parametrize, mocking, coverage
16. `fastapi_tutorial.md` — Path parameters, dependencies, background tasks, websockets

## Group 4: AI and Machine Learning Foundations
17. `transformer_architecture.md` — Attention, multi-head, encoder-decoder, scaling laws
18. `attention_mechanisms.md` — Bahdanau, Luong, scaled dot-product, Flash Attention
19. `bert_model_explained.md` — MLM, NSP, fine-tuning, variants (RoBERTa, DistilBERT)
20. `gpt_evolution.md` — GPT-1 through GPT-4, RLHF, in-context learning, open source alternatives
21. `llm_scaling_laws.md` — Kaplan, Chinchilla, emergent abilities, inference-time compute
22. `neural_network_fundamentals.md` — Perceptrons, backpropagation, optimizers, regularization
23. `natural_language_processing.md` — Tokenization, NER, dependency parsing, sentiment analysis
24. `word_embeddings_history.md` — Word2Vec, GloVe, FastText, ELMo, contextual embeddings

## Group 5: RAG and Vector Search
25. `retrieval_augmented_generation.md` — RAG pipeline, chunking, evaluation, agentic RAG
26. `faiss_vector_store.md` — Index types, IVF, HNSW, PQ, persistence, GPU acceleration
27. `nearest_neighbor_search.md` — k-NN, ANN algorithms, HNSW, LSH, FAISS index types
28. `semantic_search_techniques.md` — Dense vs sparse, HyDE, query expansion, bi/cross-encoder
29. `sentence_transformers_guide.md` — Siamese networks, models, asymmetric retrieval, fine-tuning
30. `vector_databases_comparison.md` — Pinecone, Weaviate, Qdrant, Chroma, pgvector
31. `hybrid_search_rrf.md` — BM25, RRF fusion, SPLADE, production deployment

## Group 6: Advanced ML
32. `fine_tuning_llms.md` — Full fine-tuning, LoRA, QLoRA, RLHF, DPO
33. `knowledge_distillation.md` — Soft labels, feature distillation, DistilBERT, evaluation
34. `reinforcement_learning.md` — MDP, Q-learning, DQN, PPO, RLHF, multi-agent
35. `prompt_engineering_guide.md` — Zero/few-shot, CoT, structured output, self-consistency
36. `multimodal_ai_models.md` — CLIP, VQA, image generation, document understanding
37. `graph_neural_networks.md` — Message passing, GCN, GAT, GraphSAGE, applications
38. `clustering_algorithms.md` — K-means, DBSCAN, hierarchical, GMM, evaluation
39. `dimensionality_reduction.md` — PCA, t-SNE, UMAP, applications in RAG

## Group 7: Mathematics and Theory
40. `linear_algebra_for_ml.md` — Vectors, matrix ops, SVD, eigendecomposition, attention as matmul
41. `ml_evaluation_metrics.md` — F1, AUC-ROC, BLEU, ROUGE, BERTScore, retrieval metrics

## Group 8: Systems and Infrastructure
42. `distributed_systems_fundamentals.md` — CAP theorem, consensus, replication, CRDT
43. `databases_sql_nosql.md` — ACID, indexing, MongoDB, Redis, choosing the right database
44. `api_design_rest.md` — Resources, HTTP methods, status codes, versioning, pagination
45. `microservices_patterns.md` — Service mesh, circuit breaker, Saga, observability
46. `docker_kubernetes_guide.md` — Multi-stage builds, Compose, Deployments, HPA
47. `operating_systems_basics.md` — Processes, threads, memory management, scheduling, system calls
48. `network_security_basics.md` — TLS, PKI, MITM, SQL injection, rate limiting
49. `git_version_control.md` — Object model, rebase, undoing, signed commits, hooks

## Group 9: Event-Driven and Semantic Retrieval Targets
50. `event_driven_architecture.md` — Reactor pattern, non-blocking I/O, callback chains, event streaming
51. `model_context_protocol.md` — MCP architecture, tools/resources/prompts, S7 agent integration

## Group 10: Research
52. `reproducible_research_ml.md` — Seeding, experiment tracking, DVC, model cards
53. `knowledge_graphs.md` — Triples, Wikidata, KG embeddings, GraphRAG
54. `llm_agent_architectures.md` — ReAct, memory systems, Perception→Decision→Action→Memory

## Semantic Retrieval Demonstrations

The following query/document pairs demonstrate semantic retrieval (no keyword overlap):

| Query | Target Document | Why Semantic |
|-------|----------------|--------------|
| "vector similarity search" | `nearest_neighbor_search.md` | Uses "proximity queries", "k-NN", "approximate nearest neighbor" — not "vector similarity" |
| "coroutine task scheduling" | `event_driven_architecture.md` | Uses "reactor pattern", "non-blocking I/O", "callback chain" — not "coroutine" or "asyncio" |
