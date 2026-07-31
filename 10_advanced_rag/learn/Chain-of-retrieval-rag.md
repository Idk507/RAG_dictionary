# Chain of Retrieval RAG (CoR RAG)

Chain of Retrieval (CoR) RAG is an advanced Retrieval-Augmented Generation architecture in which **retrieval is performed as a sequence of dependent retrieval steps**, where the output of one retrieval stage becomes the input for the next retrieval stage. Instead of assuming that all relevant information can be found in a single search, CoR RAG progressively expands, refines, and links evidence across multiple retrieval iterations until enough context is gathered to answer the question.

The central idea is:

> **Retrieve → Learn Something → Generate a Better Query → Retrieve Again → Continue Until the Evidence Chain Is Complete**

Unlike traditional RAG, which performs a single retrieval, CoR RAG builds an **evidence chain** where each retrieval depends on previously discovered information.

---

# Core Philosophy

Traditional RAG assumes:

```text
Question
    ↓
Retrieve Once
    ↓
Answer
```

Chain of Retrieval assumes:

```text
Question
    ↓
Retrieve
    ↓
Extract New Information
    ↓
Generate New Query
    ↓
Retrieve Again
    ↓
Repeat
    ↓
Answer
```

Each retrieval step reduces uncertainty and uncovers information that enables the next retrieval.

---

# Why Chain of Retrieval Exists

Many questions require information that cannot be found in a single document.

Example:

> **Who is the CEO of the company that acquired GitHub?**

The answer requires two connected facts:

**Step 1**

```text
GitHub
↓
Acquired by Microsoft
```

**Step 2**

```text
Microsoft
↓
CEO = Satya Nadella
```

No single retrieval necessarily contains both facts.

Instead, retrieval follows a chain.

---

# End-to-End Workflow

```text
             User Query
                  │
                  ▼
        Initial Retrieval Query
                  │
                  ▼
        Retrieve Documents (R1)
                  │
                  ▼
      Extract Intermediate Facts
                  │
                  ▼
        Generate Next Query
                  │
                  ▼
        Retrieve Documents (R2)
                  │
                  ▼
      Merge Previous Evidence
                  │
                  ▼
      More Information Needed?
            │              │
           Yes             No
            │              │
            ▼              ▼
     Generate Next Query  Generate Answer
```

The retrieval chain continues until sufficient evidence has been accumulated.

---

# Mathematical Perspective

<img width="540" height="493" alt="image" src="https://github.com/user-attachments/assets/eeedc323-e5bb-4154-8651-7e49f5309aa7" />


Each retrieval depends on the accumulated evidence.

---

# Step 1 — Initial Retrieval

The first retrieval is usually broad.

Example:

```text
Question:

Who founded the company that acquired GitHub?
```

Initial query:

```text
GitHub acquisition
```

Retriever returns:

```text
Microsoft acquired GitHub.
```

This provides only part of the answer.

---

# Step 2 — Information Extraction

The system extracts useful entities and relationships.

Retrieved fact:

```text
Microsoft acquired GitHub.
```

Extracted entity:

```text
Microsoft
```

Extracted relation:

```text
Acquired GitHub
```

These intermediate facts guide the next retrieval.

---

# Step 3 — Query Reformulation

A new query is generated from the extracted information.

Instead of:

```text
GitHub acquisition
```

the next query becomes:

```text
Microsoft founder
```

This query is much more targeted because it incorporates knowledge gained from the previous retrieval.

---

# Step 4 — Second Retrieval

The retriever searches again.

Results:

```text
Microsoft was founded by

Bill Gates

Paul Allen
```

The evidence chain is now:

```text
GitHub

↓

Microsoft

↓

Bill Gates
```

The system now has enough information to answer.

---

# Multi-Hop Retrieval

A more complex example:

Question:

> Which university did the inventor of the World Wide Web attend?

Retrieval chain:

```text
World Wide Web

↓

Inventor = Tim Berners-Lee

↓

Tim Berners-Lee biography

↓

University = Oxford

↓

Answer
```

Each retrieval reveals the information required for the next.

---

# Query Generation Function

The next query is produced by a function:

[
Q_{t+1}=g(Q,D1​,D2​,…,Dt​)
]

where:

* original query,
* previous documents,
* extracted entities,
* reasoning state,

are combined to form a better search query.

---

# Evidence Accumulation

At iteration (t):

[
E_t={D_1,D_2,…,D_t}
]

The evidence grows over time rather than being replaced.

Final generation uses:

[
LLM(Q,E_t)
]

instead of only the most recent retrieval.

---

# Retrieval Graph

Although called a "chain," some implementations naturally form a graph.

Example:

```text
Question
     │
     ▼
Microsoft
   │     │
   ▼     ▼
Founder CEO
   │      │
   ▼      ▼
Bill   Satya
```

Multiple retrieval branches may later be merged.

---

# Query Expansion

As the chain grows, queries become increasingly specific.

Iteration 1:

```text
Tesla
```

Iteration 2:

```text
Tesla founder
```

Iteration 3:

```text
Elon Musk education
```

Iteration 4:

```text
University of Pennsylvania
```

Every retrieval benefits from previous discoveries.

---

# Evidence Selection

Not every retrieved document is retained.

Documents are often scored:

[
s_i
]

Only documents with scores above a threshold:

[
s_i> τ
]

are added to the evidence chain.

This prevents low-quality information from contaminating later retrievals.

---

# Stopping Criterion

The chain ends when one of several conditions is met:

* Enough evidence has been collected.
* The answer can be generated confidently.
* No new useful information is retrieved.
* Maximum retrieval depth is reached.
* Confidence gain between iterations becomes negligible.

Conceptually,

<img width="332" height="113" alt="image" src="https://github.com/user-attachments/assets/9ee7828c-b815-4343-abee-ac7472133ec0" />


---

# Chain Depth

Different questions require different numbers of retrieval steps.

| Query Type                        | Typical Retrieval Depth |
| --------------------------------- | ----------------------: |
| Simple factual lookup             |                       1 |
| Two-hop reasoning                 |                       2 |
| Entity relationship               |                     2–3 |
| Scientific literature exploration |                     3–5 |
| Enterprise knowledge discovery    |                     4–8 |
| Complex investigative tasks       |                      5+ |

The depth is often adaptive rather than fixed.

---

# Chain Construction Strategies

Several strategies exist for building the retrieval chain:

### 1. Entity Chaining

The next query is generated from newly discovered entities.

Example:

```text
GitHub

↓

Microsoft

↓

Satya Nadella
```

---

### 2. Relation Chaining

The system follows relationships rather than entities.

Example:

```text
Author

↓

Book

↓

Publisher

↓

Headquarters
```

---

### 3. Temporal Chaining

Useful for historical questions.

Example:

```text
Company

↓

CEO 2020

↓

CEO 2022

↓

CEO Today
```

---

### 4. Citation Chaining

Frequently used in scientific literature.

```text
Paper A

↓

References

↓

Paper B

↓

References

↓

Paper C
```

---

### 5. Knowledge Graph Chaining

Each retrieval traverses edges in a graph.

```text
Person

↓

Works At

↓

Company

↓

Founder

↓

University
```

---

# Common Components

A Chain of Retrieval system often includes:

| Component         | Purpose                                          |
| ----------------- | ------------------------------------------------ |
| Initial Retriever | Performs the first retrieval                     |
| Entity Extractor  | Identifies key entities from retrieved documents |
| Query Rewriter    | Generates the next retrieval query               |
| Retriever         | Executes subsequent searches                     |
| Evidence Store    | Maintains accumulated evidence                   |
| Evidence Merger   | Combines retrieved information                   |
| Generator         | Produces the final answer                        |
| Stopping Module   | Determines when retrieval should end             |

---

# Advantages

Chain of Retrieval RAG offers several strengths:

* Excellent for **multi-hop reasoning**, where answers depend on multiple linked facts.
* Progressively improves retrieval quality by refining queries with newly acquired knowledge.
* Reduces reliance on finding a single document containing all required information.
* Enables exploration of complex entity relationships, citation networks, and knowledge graphs.
* Naturally supports iterative evidence accumulation and reasoning.

---

# Limitations

The approach also introduces trade-offs:

* Multiple retrieval rounds increase latency and infrastructure cost.
* Errors in early retrieval steps can propagate through the chain, leading to incorrect later queries.
* Determining the optimal stopping point is challenging.
* Long evidence chains may exceed context-window limits, requiring compression or summarization.
* Maintaining coherence across many retrieved documents becomes increasingly difficult as chain depth grows.

---

# Chain of Retrieval RAG vs Traditional RAG

| Aspect              | Traditional RAG       | Chain of Retrieval RAG                |
| ------------------- | --------------------- | ------------------------------------- |
| Retrieval           | Single step           | Multiple dependent steps              |
| Query generation    | Static                | Dynamically reformulated              |
| Evidence            | One retrieval result  | Accumulated across iterations         |
| Multi-hop reasoning | Limited               | Strong                                |
| Entity discovery    | Not iterative         | Progressive                           |
| Retrieval depth     | Fixed                 | Adaptive                              |
| Stopping            | After first retrieval | After sufficient evidence is gathered |

---

# Chain of Retrieval RAG vs ReAct RAG

Although both perform iterative retrieval, their primary objectives differ.

| Feature           | Chain of Retrieval RAG            | ReAct RAG                                     |
| ----------------- | --------------------------------- | --------------------------------------------- |
| Main focus        | Building an evidence chain        | Alternating reasoning and actions             |
| Retrieval         | Central mechanism                 | One possible action among many                |
| Reasoning         | Supports retrieval                | Drives all actions                            |
| Tools             | Primarily retrieval               | Retrieval, APIs, SQL, calculators, code, etc. |
| Execution pattern | Retrieve → Reformulate → Retrieve | Think → Act → Observe                         |
| Scope             | Retrieval-centric                 | General agentic reasoning                     |

**Relationship:** Chain of Retrieval can be viewed as a specialized retrieval strategy, whereas ReAct is a broader reasoning framework. A ReAct agent may internally implement a Chain of Retrieval when it repeatedly chooses retrieval actions to gather interconnected evidence.

# Research Perspective

From a research perspective, Chain of Retrieval RAG models information acquisition as a **sequential evidence discovery process**. Instead of assuming that the answer is recoverable from a single retrieval operation, it treats retrieval as a trajectory through an implicit graph of entities, relationships, citations, or documents. At iteration (t), the system uses the accumulated evidence (E_t) to generate a refined query (Q_{t+1}), retrieve new information, and expand the evidence set. This process continues until a stopping criterion indicates that sufficient evidence has been collected.

Mathematically, the approach resembles **iterative graph traversal**, **multi-hop information retrieval**, and **sequential search optimization**, where each retrieval reduces uncertainty and improves the quality of subsequent searches. As a result, Chain of Retrieval RAG is particularly effective for questions that require connecting facts across multiple documents, following citation networks, traversing knowledge graphs, or performing investigative reasoning where no single document contains the complete answer.
