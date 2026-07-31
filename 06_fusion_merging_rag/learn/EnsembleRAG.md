# Ensemble RAG (Ensemble Retrieval) — Complete Theoretical and Mathematical Explanation

Ensemble RAG is a retrieval strategy in Retrieval-Augmented Generation (RAG) where **multiple independent retrieval methods are combined into a single retrieval system** instead of relying on only one retriever.

The word **ensemble** comes from machine learning, where multiple models are combined to produce a better prediction (Random Forest, Gradient Boosting, Voting Classifier, etc.). Ensemble RAG applies the same philosophy to **information retrieval**.

Instead of asking only one retriever,

> "Which documents are relevant?"

we ask **multiple retrievers**, each using different mathematical assumptions about relevance.

Finally, all retrieved results are merged, normalized, re-ranked, and passed to the LLM.

---

# Why was Ensemble RAG invented?

To understand this, first understand the weakness of every retrieval algorithm.

Suppose the query is

> "How do transformers use positional encoding?"

### BM25

Searches exact words.

It finds

```
transformers
positional
encoding
```

If a document contains these words,
BM25 ranks it highly.

But another document might say

```
sequence position vectors
```

without using "positional encoding."

BM25 completely misses it.

---

### Dense Retriever

A dense retriever understands semantic meaning.

It may retrieve

```
Sequence information is injected using sinusoidal vectors.
```

Very relevant.

But it may ignore documents containing the exact phrase

```
Positional Encoding
```

because the embedding representation is noisy.

---

### MultiQuery Retriever

Generates several rewritten queries.

Good for recall.

Bad because it introduces many unrelated documents.

---

### HyDE

Generates a hypothetical answer first.

Works well when the original query is vague.

Fails when hypothetical document drifts from reality.

---

### Parent Document Retriever

Finds small chunks.

Returns entire parent document.

Excellent context.

Bad when parent documents are huge.

---

Each retriever solves a different problem.

None is perfect.

Ensemble Retrieval combines all their strengths.

---

# Core Philosophy

Instead of

```
Query
      ↓
Single Retriever
      ↓
Top-k
```

we build

```
                 Query
                   │
────────────────────────────────────────
│           │            │             │
BM25      Dense      MultiQuery     HyDE
│           │            │             │
Top-k     Top-k        Top-k        Top-k
│           │            │             │
────────────────────────────────────────
           Merge Results
                 │
     Score Normalization
                 │
 Duplicate Removal
                 │
 Rank Aggregation
                 │
      Final Top-k
                 │
         LLM Context
```

Notice there are multiple independent retrieval pipelines.

---

# Mathematical View

Assume

Corpus

<img width="220" height="51" alt="image" src="https://github.com/user-attachments/assets/cb2e76ce-5c4d-416e-8375-ecad483b2c46" />


Query


q


Instead of one retrieval function


R(q)


we define


m


retrievers

<img width="181" height="58" alt="image" src="https://github.com/user-attachments/assets/bab6bf2c-4631-436d-b179-ee4bf6a4736a" />


Each returns

<img width="187" height="60" alt="image" src="https://github.com/user-attachments/assets/393d94ea-f598-4570-a053-38363d3b7c99" />

where

* document
* retrieval score

Example

BM25

```
A 12.4
B 11.7
C 10.5
```

Dense

```
C 0.93
D 0.91
A 0.88
```

HyDE

```
D 0.95
E 0.94
```

These scores are not comparable.

BM25 ranges

```
0-50
```

Dense similarity

```
0-1
```

Need normalization.

---

# Step 1 — Independent Retrieval

Each retriever uses completely different mathematics.

---

## Sparse Retriever

Uses TF-IDF / BM25.

Similarity


Score_{BM25}(q,d)


---

## Dense Retriever

Embeddings

<img width="535" height="221" alt="image" src="https://github.com/user-attachments/assets/4f5b66db-8601-4078-88ca-41091149b314" />


---

## MultiQuery

Produces

<img width="132" height="41" alt="image" src="https://github.com/user-attachments/assets/f78bde65-5d62-4ae9-9745-0cc740921d1e" />

Each query retrieves


R(q_i)


Union all results.

---

## HyDE

Produces

Hypothetical document


H(q)


Embedding


e_H


Search


cos(e_H,e_d)


---

Every retriever independently estimates relevance.

---

# Step 2 — Candidate Union

Suppose

BM25

```
A B C
```

Dense

```
C D E
```

HyDE

```
D E F
```

Union

```
A
B
C
D
E
F
```

This increases recall dramatically.

---

# Step 3 — Score Normalization

This is one of the most important parts.

Different retrievers produce different score scales.

Need


s_i'


normalized.

---

## Min-Max Normalization


<img width="270" height="63" alt="image" src="https://github.com/user-attachments/assets/f897cad0-9dfe-4074-a68e-3dae95c756cd" />


Now

Every score

```
0
```

to

```
1
```

---

## Z-score

<img width="136" height="55" alt="image" src="https://github.com/user-attachments/assets/a08579ea-1a42-435b-8b65-e13f03dc5354" />


Useful if distributions differ.

---

## Rank-based Normalization

Ignore raw score.

Only ranking matters.

Example

```
Rank1 =1
Rank2 =2
Rank3 =3
```

---

# Step 4 — Rank Aggregation

Now combine rankings.

Several algorithms exist.

---

# Method 1 — Weighted Sum

Each retriever gets weight


w_i


Final score

<img width="235" height="63" alt="image" src="https://github.com/user-attachments/assets/29c21dda-f7a9-4793-8c46-2a77e20b9a64" />


Example

BM25 weight

0.3

Dense

0.5

HyDE

0.2

Document

```
BM25 =0.9
Dense=0.8
HyDE=0.7
```

Final


0.3(0.9)+0.5(0.8)+0.2(0.7)=0.81


---

# Method 2 — Reciprocal Rank Fusion (RRF)

The most popular ensemble algorithm.

Instead of scores,

use ranks.

Formula

<img width="257" height="80" alt="image" src="https://github.com/user-attachments/assets/c528962b-1b4b-4cbd-b10b-517110df52d6" />


where

* (r_i(d)) is the rank assigned by retriever (i)
* (k) is a smoothing constant (commonly around 60)

Example

Retriever1

```
A rank1
```

Retriever2

```
A rank4
```

Retriever3

```
A rank2
```

Score

<img width="158" height="72" alt="image" src="https://github.com/user-attachments/assets/2d08b5af-4515-4592-82ee-e196b130886a" />


Higher score means higher overall ranking.

---

## Why RRF Works

Suppose

Dense gives

```
Rank1
```

BM25

```
Rank20
```

Average score methods might over-penalize the document.

RRF still rewards it because appearing near the top in **any** retriever contributes significantly.

This makes RRF robust to incomparable score distributions and is why it is widely used in ensemble retrieval research.

---

# Method 3 — Borda Count

Each rank receives points.

Rank1

100

Rank2

99

...

Total votes determine ranking.

This comes from voting theory.

---

# Method 4 — Learning-to-Rank

Instead of handcrafted fusion,

train a ranking model.

Input features

* BM25 score
* cosine similarity
* reranker score
* document length
* recency
* metadata quality
* click history

Output

Probability of relevance.

Models include LambdaMART, RankNet, and neural ranking architectures.

---

# Step 5 — Duplicate Removal

Multiple retrievers often return identical chunks.

Example

BM25

```
Chunk 17
```

Dense

```
Chunk 17
```

Need deduplication.

Common approaches:

* Exact document ID matching.
* Hash-based matching on normalized text.
* Near-duplicate detection using embedding similarity or MinHash/LSH for large corpora.

---

# Step 6 — Final Top-k Selection

After fusion,

sort

```
Score descending
```

Take

```
Top-k
```

Those documents become LLM context.

---

# Complete Workflow

```
User Query
      │
      ▼
─────────────────────────────────────────────
│ BM25 Retriever                           │
│ Dense Retriever                          │
│ MultiQuery Retriever                     │
│ HyDE Retriever                           │
│ Parent Retriever                         │
│ Metadata Filter                          │
─────────────────────────────────────────────
      │
      ▼
Candidate Documents
      │
      ▼
Merge Union
      │
      ▼
Remove Duplicates
      │
      ▼
Normalize Scores
      │
      ▼
Rank Fusion
      │
      ▼
Optional Cross-Encoder Re-ranker
      │
      ▼
Top-k Documents
      │
      ▼
Prompt Construction
      │
      ▼
Large Language Model
      │
      ▼
Generated Answer
```

---

# Ensemble Strategies

## Parallel Ensemble

Every retriever runs simultaneously.

```
Query
 │
 ├──BM25
 ├──Dense
 ├──HyDE
 └──MultiQuery
```

Fast when parallel execution is available, but computationally more expensive.

---

## Sequential Ensemble

One retriever feeds another.

```
BM25
   ↓
Dense
   ↓
Reranker
```

Useful when you want to reduce candidate sets progressively.

---

## Hierarchical Ensemble

```
Query
     │
 Sparse + Dense
      │
 Merge
      │
 Parent Retrieval
      │
 Reranker
```

Different retrieval stages focus on different tasks.

---

## Adaptive Ensemble

The system decides which retrievers to invoke based on query characteristics.

Examples:

* Keyword-heavy queries → emphasize BM25.
* Semantic or natural-language questions → emphasize dense retrieval.
* Ambiguous queries → add MultiQuery or HyDE.
* Structured filters → emphasize metadata retrieval.

This reduces latency while preserving quality.

---

# Computational Complexity

Let:

* (m): number of retrievers.
* (k): candidates returned per retriever.
* (N): corpus size.

Ignoring index construction:

* Sparse retrieval: approximately (O(\log N + k)) with inverted indexes.
* Dense ANN retrieval: depends on the index (e.g., HNSW traversal is typically sublinear in practice).
* Candidate fusion: (O(mk)).
* Sorting merged candidates: (O(M \log M)), where (M \le mk).

The main trade-off is higher retrieval cost in exchange for improved recall and robustness.

---

# Advantages

* Combines lexical and semantic matching.
* Significantly improves recall across diverse query types.
* More robust than any individual retriever.
* Reduces the impact of weaknesses in a single retrieval algorithm.
* Easily extensible by adding specialized retrievers.

---

# Limitations

* Higher latency because multiple retrievers are executed.
* Increased infrastructure and maintenance complexity.
* Requires careful score normalization or rank-fusion strategies.
* May retrieve many redundant candidates without effective deduplication.
* Memory and compute costs increase with the number of retrievers.

---

# Real-World Applications

Ensemble retrieval is widely used in production RAG systems where accuracy is more important than relying on a single retrieval paradigm. Typical applications include:

* Enterprise search across heterogeneous documents, where BM25 captures exact terminology while dense retrieval captures semantic matches.
* Legal and compliance assistants, where exact citations and semantically related precedents are both essential.
* Biomedical literature search, combining keyword-based retrieval of technical terms with semantic retrieval of conceptually related research.
* Customer support systems, where metadata filters, FAQ retrieval, and semantic search complement one another.
* Code assistants, combining lexical code search with embedding-based retrieval over documentation and repositories.

---

# Relationship to Other RAG Variants

Ensemble RAG is **not a competing retrieval algorithm**; it is a **meta-retrieval framework**. It can incorporate many of the retrieval methods you have studied:

| RAG Variant                | Can be part of an Ensemble? | Role                                        |
| -------------------------- | --------------------------- | ------------------------------------------- |
| Sparse (BM25) RAG          | ✔                           | Lexical retrieval                           |
| Dense Retrieval RAG        | ✔                           | Semantic retrieval                          |
| Hybrid Retrieval RAG       | ✔                           | One ensemble component or a baseline fusion |
| MultiQuery RAG             | ✔                           | Query expansion for higher recall           |
| HyDE RAG                   | ✔                           | Hypothetical document retrieval             |
| Parent Document Retriever  | ✔                           | Context expansion                           |
| Contextual Compression RAG | ✔                           | Post-retrieval context reduction            |
| Knowledge Graph RAG        | ✔                           | Graph-based evidence retrieval              |
| Query-Aware RAG            | ✔                           | Adaptive retriever selection or weighting   |

Conceptually, Ensemble RAG sits at a higher architectural level: it orchestrates multiple retrieval mechanisms, fuses their outputs using techniques such as weighted score fusion or Reciprocal Rank Fusion, and optionally applies a neural re-ranker before passing the final evidence to the LLM. This flexibility is why modern production RAG systems often employ ensemble retrieval rather than relying on a single retrieval strategy.
