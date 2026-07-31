# LLM-Based Query-Aware RAG (Query-Adaptive Retrieval-Augmented Generation)

LLM-Based Query-Aware RAG is an advanced Retrieval-Augmented Generation (RAG) architecture in which the **Large Language Model (LLM) actively participates before retrieval** to understand the user's intent, transform the query, and optimize the retrieval process. Instead of sending the user's raw question directly to a retriever, the system first asks the LLM to analyze the query and produce a retrieval-optimized representation.

Traditional RAG assumes the user's query is already suitable for retrieval. Query-aware RAG recognizes that **human language and retrieval language are often different**. Humans ask vague, conversational, ambiguous, or incomplete questions, whereas retrievers work best with precise semantic representations.

The LLM acts as an **intelligent query optimizer**.

---

# Motivation

Consider a user asking

> "Who invented it and when?"

A normal retriever cannot answer because:

* "it" has no meaning.
* The subject is missing.
* Dense embeddings become ambiguous.
* BM25 cannot find matching keywords.

A Query-Aware RAG system first asks

> What does "it" refer to?

or infers from conversation history that

> "it" = Transformer architecture

Then retrieval becomes

> "Who invented the Transformer architecture and when was it introduced?"

Only after this optimization does retrieval begin.

Therefore,

Traditional RAG

```
User Query
      ↓
Retriever
      ↓
Documents
      ↓
LLM
```

Query-Aware RAG

```
User Query
      ↓
LLM analyzes query
      ↓
Optimized Retrieval Query
      ↓
Retriever
      ↓
Documents
      ↓
LLM
```

Notice that the LLM appears **twice**:

* Before retrieval
* After retrieval

---

# Core Philosophy

Instead of assuming

[
Q_{user}=Q_{retrieval}
]

Query-Aware RAG assumes

[
Q_{retrieval}=f_{LLM}(Q_{user})
]

where

* (Q_{user}) = original question
* (Q_{retrieval}) = optimized retrieval query
* (f_{LLM}) = reasoning function of the LLM

---

# Complete Workflow

The workflow contains multiple reasoning stages.

```
User
   │
   ▼
Original Query
   │
   ▼
LLM Query Understanding
   │
   ▼
Intent Detection
   │
   ▼
Query Classification
   │
   ▼
Query Reformulation
   │
   ▼
Query Expansion
   │
   ▼
Retriever
   │
   ▼
Ranking
   │
   ▼
Retrieved Context
   │
   ▼
Answer Generation
```

Let's study every stage.

---

# Step 1: User Query

Suppose the user asks

> Why is GPT better than BERT for reasoning?

This is not what the retriever should necessarily receive.

Instead the system first analyzes it.

---

# Step 2: LLM Query Understanding

This is the most important stage.

The LLM performs semantic reasoning.

It predicts

* user intent
* entities
* relationships
* missing information
* ambiguity
* retrieval difficulty
* required knowledge type

Instead of viewing the query as text,

the LLM builds a semantic representation.

For example

```
Question:

Why is GPT better than BERT for reasoning?

↓

Intent:
Comparison

↓

Entity A:
GPT

↓

Entity B:
BERT

↓

Aspect:
Reasoning capability

↓

Need:
Comparison documents
```

This internal reasoning never appears to the user.

---

# Mathematical Representation

Let

<img width="240" height="56" alt="image" src="https://github.com/user-attachments/assets/a781d43c-6f8c-4b7d-964b-b9f00a048116" />


The LLM maps

<img width="91" height="38" alt="image" src="https://github.com/user-attachments/assets/9fec016d-abcc-4a3f-87d2-bd350eb9e85f" />


where

<img width="527" height="47" alt="image" src="https://github.com/user-attachments/assets/be3e5089-64dd-4169-a215-a90f4d99cf71" />


This intermediate representation is much richer than the original sentence.

---

# Step 3: Intent Detection

The system predicts the query type.

Possible intents include:

* Definition
* Comparison
* Summarization
* Temporal
* Multi-hop reasoning
* Calculation
* Recommendation
* Explanation
* Fact lookup
* Procedural
* Analytical

Example

Query

> Compare FAISS and Pinecone

Intent

```
Comparison
```

Example

Query

> What is RAG?

Intent

```
Definition
```

Example

> How does RAG work internally?

Intent

```
Explanation
```

Different intents require different retrieval strategies.

---

# Mathematical View

Intent classification


P(Intent|Q)


The LLM estimates

<img width="167" height="47" alt="image" src="https://github.com/user-attachments/assets/f8ca9f5b-ff11-4a79-bb34-3c47f6769f19" />


---

# Step 4: Entity Extraction

The LLM extracts entities.

Example

```
Explain LangChain RetrievalQA
```

Entities

```
LangChain

RetrievalQA
```

Another example

```
Who created LlamaIndex?
```

Entities

```
LlamaIndex
```

These entities become retrieval anchors.

---

# Step 5: Query Disambiguation

Example

```
Apple revenue
```

Does Apple mean

* fruit
* Apple Inc.

The LLM determines

```
Technology company
```

Another example

```
Python list
```

Programming language?

or

animal?

The LLM resolves ambiguity.

---

# Step 6: Query Expansion

Now the LLM enriches the query.

Original

```
LLM memory
```

Expanded

```
Long-term memory
Conversation memory
Persistent memory
Context window
Memory architectures
```

Expansion improves recall.

Mathematically

Original


Q


becomes

<img width="372" height="52" alt="image" src="https://github.com/user-attachments/assets/3e75ed67-8bd9-43b4-98be-bf2f87f128c6" />


---

# Step 7: Query Reformulation

Sometimes the wording itself is poor.

Original

```
How GPT remembers stuff
```

Rewritten

```
How do GPT models maintain conversational context using context windows and memory mechanisms?
```

This is much easier for retrieval.

---

# Step 8: Query Decomposition

Complex questions become smaller questions.

Example

```
Compare GPT-4 with Gemini and Claude on reasoning benchmarks.
```

↓

Subquery 1

```
GPT-4 reasoning benchmarks
```

Subquery 2

```
Gemini reasoning benchmarks
```

Subquery 3

```
Claude reasoning benchmarks
```

Each retrieves independently.

---

# Mathematical Formulation

Original


Q


becomes

<img width="223" height="43" alt="image" src="https://github.com/user-attachments/assets/5fd4025b-e254-4881-9419-9902ca060267" />


Each

q_i


has its own retrieval.

---

# Step 9: Retrieval Strategy Selection

The LLM may decide which retrieval method fits best.

For example:

Simple factual lookup:

```
BM25
```

Semantic question:

```
Dense Retrieval
```

Mixed query:

```
Hybrid Retrieval
```

Multi-hop reasoning:

```
Graph Retrieval
```

Long document:

```
Parent Document Retriever
```

The query itself determines the retriever.

---

# Step 10: Embedding Generation

The optimized query becomes an embedding.


e_q = Encoder(Q')


Every document embedding


e_d


already exists.

Similarity


S(q,d) = cos(e_q,e_d)


---

# Cosine Similarity

<img width="182" height="58" alt="image" src="https://github.com/user-attachments/assets/18f36e2f-ba78-4735-87f6-076b59f9271a" />


Higher similarity

↓

Higher retrieval score.

---

# Step 11: Document Ranking

Every retrieved document receives a score.

Example

<img width="468" height="50" alt="image" src="https://github.com/user-attachments/assets/818885bd-dfd8-4b9a-9c99-8b47271abc36" />

or

<img width="292" height="45" alt="image" src="https://github.com/user-attachments/assets/c1884a8d-99fe-4cdf-84d0-abef46e3f9b8" />


where a cross-encoder jointly processes the query and document for more accurate ranking.

---

# Step 12: Context Construction

The selected chunks are combined.

```
Chunk A

Chunk B

Chunk C

Chunk D
```

They form

```
Retrieved Context
```

---

# Step 13: Answer Generation

The second LLM call now receives

```
Question

+

Retrieved Context
```

Prompt

```
Question

Retrieved Documents

Generate answer only using context.
```

---

# Mathematical Objective

The model estimates


P(A|Q,C)


where

* (Q) = optimized query
* (C) = retrieved context
* (A) = answer

---

# Complete Mathematical Pipeline


Q_{user}


↓

LLM


Q_{optimized} = f(Q_{user})


↓

Embedding


e_q = Encoder(Q_{optimized})


↓

Similarity


Score_i = Similarity(e_q,e_i)


↓

Top-k


D_k


↓

Generator


Answer = LLM(Q,D_k)


---

# Types of Query Transformations

An LLM may apply one or more of the following:

| Transformation | Example                                                         |
| -------------- | --------------------------------------------------------------- |
| Rewrite        | "GPT memory" → "How GPT models maintain conversational context" |
| Expand         | Add synonyms and related concepts                               |
| Decompose      | Split into multiple focused questions                           |
| Clarify        | Resolve ambiguous references like "it" or "they"                |
| Summarize      | Compress overly long user input into a concise retrieval query  |
| Normalize      | Standardize spelling, abbreviations, and terminology            |
| Add Context    | Incorporate conversation history or inferred constraints        |

---

# Advantages

LLM-Based Query-Aware RAG offers several benefits:

* Higher retrieval precision by aligning queries with document language.
* Better recall through expansion and synonym generation.
* Improved handling of ambiguous, incomplete, or conversational questions.
* Support for complex, multi-hop reasoning via query decomposition.
* Dynamic selection of retrieval strategies based on intent.
* Better use of conversation history for contextual retrieval.

---

# Limitations

Despite its strengths, there are trade-offs:

* **Additional latency:** At least one extra LLM call is made before retrieval.
* **Higher cost:** Query transformation consumes tokens and compute.
* **Propagation of reasoning errors:** Incorrect reformulation or expansion can reduce retrieval quality.
* **Over-expansion risk:** Adding too many loosely related terms can introduce irrelevant documents and reduce precision.
* **Prompt sensitivity:** The quality of the optimized query depends on the prompt and capabilities of the query-rewriting LLM.

---

# Relationship to Other RAG Variants

LLM-Based Query-Aware RAG is a foundational capability that often complements other RAG architectures rather than replacing them.

| RAG Variant         | Primary Focus                                         | Relationship to Query-Aware RAG                                                              |
| ------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Naive RAG           | Direct retrieval from raw user query                  | Query-Aware RAG replaces the raw query with an optimized one before retrieval.               |
| Query Expansion RAG | Add synonyms or related terms                         | Often implemented as one step within a query-aware pipeline.                                 |
| HyDE RAG            | Generate a hypothetical answer/document for retrieval | HyDE is a specialized form of LLM-driven query transformation.                               |
| Multi-Query RAG     | Generate multiple retrieval queries                   | A natural extension of query-aware reasoning when one reformulated query is insufficient.    |
| Self-RAG            | LLM evaluates retrieval and generation quality        | Adds post-retrieval self-reflection in addition to pre-retrieval query optimization.         |
| Adaptive RAG        | Dynamically choose retrieval workflows                | Query-aware intent analysis can provide the signals used for adaptation.                     |
| Agentic RAG         | Multi-step planning with tools                        | Query-aware reasoning is often the first planning stage before tool selection and retrieval. |

---

# End-to-End Conceptual Pipeline

```text
                USER QUESTION
                      │
                      ▼
        ┌────────────────────────┐
        │  LLM Query Analysis    │
        │ • Intent detection     │
        │ • Entity extraction    │
        │ • Ambiguity resolution │
        │ • Context inference    │
        └────────────────────────┘
                      │
                      ▼
        ┌────────────────────────┐
        │ Query Transformation   │
        │ • Rewrite              │
        │ • Expand               │
        │ • Decompose            │
        │ • Normalize            │
        └────────────────────────┘
                      │
                      ▼
             Optimized Query(ies)
                      │
                      ▼
        ┌────────────────────────┐
        │ Retrieval Layer        │
        │ • BM25                 │
        │ • Dense Retrieval      │
        │ • Hybrid Retrieval     │
        │ • Graph Retrieval      │
        └────────────────────────┘
                      │
                      ▼
          Candidate Documents/Chunks
                      │
                      ▼
        ┌────────────────────────┐
        │ Ranking & Filtering    │
        │ • Similarity scoring   │
        │ • Cross-encoder rerank │
        │ • Context selection    │
        └────────────────────────┘
                      │
                      ▼
             Retrieved Context
                      │
                      ▼
        ┌────────────────────────┐
        │ Answer Generation LLM  │
        │ P(Answer | Query, Ctx) │
        └────────────────────────┘
                      │
                      ▼
                 FINAL ANSWER
```

## Research Perspective

From a research standpoint, LLM-Based Query-Aware RAG addresses the **query-document distribution mismatch** problem. Documents are typically written in formal, information-rich language, while user queries are often short, ambiguous, or conversational. By learning a transformation (f_{\text{LLM}}: Q_{\text{user}} \rightarrow Q_{\text{retrieval}}), the system shifts the query into a representation that is more compatible with the retriever's embedding space or lexical matching mechanism. This generally increases retrieval effectiveness (precision and recall), particularly for ambiguous, compositional, and multi-hop questions. Modern production RAG systems frequently combine query-aware techniques with hybrid retrieval, reranking, contextual compression, and adaptive retrieval policies, making query understanding one of the most influential stages in the overall RAG pipeline.
