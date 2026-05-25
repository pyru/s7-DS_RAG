# Knowledge Graphs: Representing Structured World Knowledge

A knowledge graph (KG) represents information as a network of entities (nodes) connected by typed relationships (edges). The fundamental unit is the **triple**: (subject, predicate, object) or (head entity, relation, tail entity).

## Core Concepts

**Triple examples**:
- (Barack Obama, bornIn, Honolulu)
- (Python, isA, ProgrammingLanguage)
- (BERT, developedBy, Google)
- (Shannon, authorOf, "A Mathematical Theory of Communication")

**Entity types**: Persons, places, organizations, concepts, events, biological entities

**Relation types**: is-a, part-of, located-in, developed-by, authored-by, born-in, connected-to

**RDF (Resource Description Framework)**: W3C standard for representing KG triples using URIs. SPARQL is the query language.

## Major Knowledge Graphs

**Wikidata**: Open collaborative knowledge base with 100M+ items. All Wikipedia infoboxes are sourced from Wikidata. SPARQL endpoint available.

**Google Knowledge Graph**: Powers Google Search's knowledge panels. ~500 billion facts. Proprietary.

**DBpedia**: Structured data extracted from Wikipedia infoboxes. Freely available.

**Freebase** (deprecated, absorbed into Wikidata): Pioneered structured entity data.

**Domain-specific graphs**: Gene Ontology (biology), UMLS (medicine), WordNet (linguistics), FinKB (finance).

## Knowledge Graph Construction

**Manual curation**: Expert knowledge engineers. Highest quality, lowest scale (IBM's early KG).

**Automated extraction**: Information extraction from text using NLP:
- Named Entity Recognition (NER)
- Relation Extraction (RE)
- Coreference Resolution

**Schema.org markup**: Webmasters annotate their content with structured markup that search engines consume.

**Neural KG extraction**: LLMs prompted to extract triples from text:
```
Text: "Marie Curie was born in Warsaw in 1867 and won the Nobel Prize in Physics in 1903."
Triples: (Marie Curie, birthPlace, Warsaw), (Marie Curie, birthYear, 1867), 
         (Marie Curie, award, Nobel Prize in Physics), (Marie Curie, awardYear, 1903)
```

## Knowledge Graph Embeddings

KG embeddings map entities and relations to continuous vectors for:
- **Link prediction**: Predict missing relations (is A related to B by R?)
- **Entity alignment**: Match entities across different KGs
- **Question answering**: Convert natural language to structured queries

**TransE**: Entity embeddings such that h + r ≈ t for true triples. Simple but effective.

**RotatE**: Relations as rotations in complex space — handles symmetry, antisymmetry, inversion.

**RGCN (Relational GCN)**: Graph neural network approach respecting relation types.

## KGs in RAG Systems

Knowledge graphs enhance RAG by:

1. **Entity-centric retrieval**: "Tell me about Claude Shannon" → retrieve all triples where Shannon is subject/object
2. **Multi-hop reasoning**: "Where was the inventor of information theory born?" → (Shannon, authorOf, InfoTheory) → (Shannon, birthPlace, Petoskey)
3. **Structured fact grounding**: Verify LLM claims against KG facts
4. **Schema validation**: Ensure generated text respects known entity types and relations

**GraphRAG** (Microsoft Research): Clusters the knowledge graph into communities, generates summaries of each community, enables hierarchical retrieval from cluster-level to entity-level.

## SPARQL Example

```sparql
SELECT ?person ?birthPlace
WHERE {
  ?person a dbo:Scientist .
  ?person dbo:birthPlace ?birthPlace .
  ?person dbo:knownFor dbr:Information_theory .
}
LIMIT 10
```

Returns: Claude Shannon → Petoskey, Michigan (from DBpedia)
