# Modular RAG: Complete Research-Level Explanation

The term **Modular RAG** does **not** refer to a new retrieval algorithm like HyDE, GraphRAG, RAPTOR, or Cog-RAG. Instead, it is an **architectural paradigm** introduced in the paper **"Modular RAG: Transforming RAG Systems into LEGO-like Reconfigurable Frameworks" (2024)**. Its purpose is to redefine how RAG systems are designed by treating every capability as an independent, composable module rather than enforcing a fixed retrieve-then-generate pipeline. ([arXiv][1])

In other words:

> **Traditional RAG asks:** *How do we retrieve documents?*
> **Modular RAG asks:** *How should we architect an entire RAG system so every component can be independently replaced, reordered, routed, or reused?* ([arXiv][1])

---

# Why Modular RAG Was Proposed

The original RAG architecture is very simple:

```text
Query
   │
   ▼
Retriever
   │
   ▼
Top-k Documents
   │
   ▼
LLM
   │
   ▼
Answer
```

This worked well initially.

However, over the last few years, researchers introduced many improvements:

* Query Rewriting
* HyDE
* Multi-query Retrieval
* Hybrid Retrieval
* GraphRAG
* RAPTOR
* Parent Retriever
* Rerankers
* Context Compression
* Memory
* Agents
* Reflection
* Verification

Eventually, a production RAG system looked like:

```text
Query

↓

Query Rewrite

↓

HyDE

↓

Hybrid Retrieval

↓

Multi Query

↓

Fusion

↓

Reranking

↓

Compression

↓

Prompt Builder

↓

LLM

↓

Verification
```

The problem is that there is **no longer a single RAG pipeline**.

Every application requires different components.

The paper argues that the classical **Retrieve → Generate** abstraction is no longer sufficient to describe modern RAG systems. ([arXiv][1])

---

# The Main Philosophy

Instead of building one large pipeline,

build independent modules.

Think of LEGO blocks.

```text
Retriever

Reranker

Memory

Compressor

Generator

Router

Verifier

Planner
```

Each module has

* clear input
* clear output
* independent implementation

and can be connected in arbitrary ways.

---

# Module Definition

A module is simply

```text
Input

↓

Transformation

↓

Output
```

Every module performs exactly one responsibility.

For example

Retriever

```text
Query

↓

Retriever

↓

Documents
```

Compression

```text
Documents

↓

Compression

↓

Smaller Documents
```

Generator

```text
Context

↓

LLM

↓

Answer
```

Instead of one enormous algorithm,

Modular RAG becomes

```text
Module

↓

Module

↓

Module
```

---

# Architecture

The paper divides a RAG system into independent functional components.

A typical Modular RAG architecture looks like:

```text
User Query
     │
     ▼
Query Processing Module
     │
     ▼
Routing Module
     │
     ▼
Retrieval Module
     │
     ▼
Fusion Module
     │
     ▼
Reranking Module
     │
     ▼
Compression Module
     │
     ▼
Prompt Construction Module
     │
     ▼
Generation Module
     │
     ▼
Verification Module
     │
     ▼
Final Response
```

Notice that retrieval is just **one module** among many.

---

# Core Modules

The paper identifies several reusable module categories.

---

## 1. Query Processing Module

Purpose:

Improve the incoming query before retrieval.

Techniques include:

* Query rewriting
* Query expansion
* HyDE
* Multi-query generation
* Decomposition

Input

```text
User Query
```

Output

```text
Optimized Query
```

---

## 2. Retrieval Module

Responsible only for retrieving knowledge.

It may use

* BM25
* Dense Retrieval
* Hybrid Retrieval
* Graph Retrieval
* Knowledge Graph
* SQL
* APIs
* Web Search

The rest of the pipeline does not care which retrieval algorithm is used.

Only the interface matters.

```text
Query

↓

Retriever

↓

Documents
```

---

## 3. Routing Module

One of the major additions of Modular RAG.

Instead of sending every query through the same pipeline,

the router chooses.

Example

```text
Question

↓

Router

↓

Simple Question?

↓

YES

↓

BM25

NO

↓

GraphRAG
```

Another example

```text
Medical Question

↓

Medical Database

Financial Question

↓

Financial Database

Programming

↓

Code Repository
```

Routing enables specialized pipelines.

---

## 4. Fusion Module

Sometimes multiple retrievers run simultaneously.

Example

```text
BM25

Dense Retrieval

Knowledge Graph

Web Search
```

Each returns different results.

Fusion combines them.

Possible techniques

* Reciprocal Rank Fusion (RRF)
* Weighted Fusion
* Score Fusion
* Union
* Voting

Fusion improves recall before later filtering.

---

## 5. Reranking Module

After retrieval,

documents are reordered.

Input

```text
20 Documents
```

Output

```text
Top 5 Best Documents
```

Common techniques

* Cross-Encoder rerankers
* LLM reranking
* ColBERT
* FlashRank

The retriever optimizes **recall**; the reranker optimizes **precision**.

---

## 6. Compression Module

Retrieved documents are often too large.

Compression removes irrelevant content.

Methods include

* LLM extraction
* Contextual Compression
* Sentence selection
* Token pruning

Result

```text
10 Pages

↓

Relevant Paragraphs
```

This reduces context-window usage.

---

## 7. Prompt Construction Module

Combines

* Question
* Retrieved Context
* Instructions
* System Prompt
* Metadata

into the final prompt sent to the LLM.

---

## 8. Generation Module

Standard LLM generation.

Possible models

* GPT
* Claude
* Gemini
* Llama
* Mistral

This module is interchangeable.

---

## 9. Verification Module

Optional.

Checks

* Hallucination
* Citation correctness
* Faithfulness
* Confidence

If verification fails,

another module may be invoked.

---

# Operators

Modules alone are not enough.

The paper introduces **operators** that define **how modules interact**. ([arXiv][1])

These operators are the real novelty.

Instead of a fixed pipeline,

operators control execution.

---

## Sequential Operator

Traditional RAG.

```text
A

↓

B

↓

C

↓

D
```

Everything executes in order.

---

## Parallel Operator

Run multiple modules simultaneously.

```text
             Query

          /    |    \

      BM25 Dense KG

          \    |    /

           Fusion
```

Reduces latency and improves coverage.

---

## Conditional Operator

Branch based on conditions.

```text
Simple Query?

YES

↓

Vector Search

NO

↓

GraphRAG
```

Only one branch executes.

---

## Loop Operator

Repeat until satisfied.

```text
Retrieve

↓

Enough Context?

↓

No

↓

Retrieve Again
```

Useful for iterative retrieval.

---

## Selection Operator

Choose the best among alternatives.

Example

```text
Three Retrievers

↓

Best Retrieval

↓

Continue
```

---

## Ensemble Operator

Keep all outputs.

Combine later.

```text
Retriever A

Retriever B

Retriever C

↓

Merge
```

---

# Execution Patterns

The paper groups Modular RAG systems into four recurring orchestration patterns. ([arXiv][1])

## 1. Linear Pattern

Classic pipeline.

```text
A

↓

B

↓

C

↓

D
```

Best for simple QA.

---

## 2. Conditional Pattern

Branching logic.

```text
Router

↓

Medical

↓

Medical Retriever

Legal

↓

Legal Retriever
```

Different questions use different workflows.

---

## 3. Branching Pattern

Execute multiple branches simultaneously.

```text
Query

↓

Dense

Sparse

Graph

↓

Fusion
```

This is ideal when combining complementary retrieval strategies.

---

## 4. Looping Pattern

Iterative execution.

```text
Retrieve

↓

Evaluate

↓

Need More?

↓

Yes

↓

Retrieve Again
```

Supports adaptive retrieval and self-improvement.

---

# Why Is It Called "LEGO-like"?

The paper compares modules to LEGO bricks.

Imagine replacing only the retriever.

Old

```text
BM25
```

New

```text
GraphRAG
```

Nothing else changes.

Or replace

```text
GPT-4
```

with

```text
Claude
```

Again,

nothing else changes.

Each component has a well-defined interface, so implementations can be swapped without redesigning the entire system. ([arXiv][1])

---

# How It Is Implemented

A production implementation usually consists of independent services or libraries.

```text
                 User Query
                      │
                      ▼
          Query Processing Service
                      │
                      ▼
               Router Service
          ┌───────────┴────────────┐
          ▼                        ▼
 Dense Retriever            BM25 Retriever
          └───────────┬────────────┘
                      ▼
                Fusion Service
                      ▼
              Reranker Service
                      ▼
             Compression Service
                      ▼
          Prompt Builder Service
                      ▼
                 LLM Service
                      ▼
           Verification Service
                      ▼
                 Final Answer
```

Each box exposes a clear input/output contract, making it independently deployable, testable, and replaceable.

---

# Advantages

Modular RAG provides several engineering benefits:

* High flexibility: components can be replaced independently.
* Easy experimentation: compare retrieval or generation modules without rewriting the system.
* Extensibility: add new capabilities such as memory, verification, or planning as new modules.
* Better maintainability through separation of concerns.
* Reuse of modules across multiple applications.
* Support for heterogeneous data sources and specialized retrieval strategies.
* Easier benchmarking and ablation because modules have well-defined interfaces. ([arXiv][1])

---

# Limitations

Modularity also introduces trade-offs:

* More orchestration logic is required.
* Routing decisions become critical for quality.
* Additional modules can increase latency.
* Inter-module interfaces must be carefully designed.
* Observability, debugging, and tracing become more important as workflows grow more complex.
* Poorly composed pipelines may negate the benefits of strong individual modules.

---

# Comparison with Other RAG Architectures

| Architecture    | Main Innovation                                                                       |
| --------------- | ------------------------------------------------------------------------------------- |
| Standard RAG    | Retrieve → Generate pipeline                                                          |
| Hybrid RAG      | Multiple retrieval methods                                                            |
| GraphRAG        | Graph-based knowledge retrieval                                                       |
| RAPTOR          | Hierarchical document summarization and retrieval                                     |
| Cog-RAG         | Dual-hypergraph theme/entity retrieval                                                |
| Agentic RAG     | LLM agents plan and invoke tools                                                      |
| Adaptive RAG    | Query-dependent retrieval strategy                                                    |
| **Modular RAG** | Reconfigurable architecture composed of interchangeable modules and control operators |

---

# End-to-End Workflow

```text
User Query
      │
      ▼
Query Processing
      │
      ▼
Router
      │
      ├──────────────┐
      ▼              ▼
Retriever A    Retriever B
      │              │
      └──────┬───────┘
             ▼
          Fusion
             ▼
        Reranking
             ▼
       Compression
             ▼
      Prompt Builder
             ▼
       LLM Generation
             ▼
       Verification
             ▼
       Final Response
```

These four modules are **post-retrieval modules** in a Modular RAG pipeline. They are **not mandatory**—they are optional building blocks that improve answer quality, reduce cost, and increase reliability. Let's examine each in detail.

---

# 1. Compression Module

## Why is it needed?

After retrieval, you may have something like this:

```text
Retriever Output

Document 1 → 3 pages
Document 2 → 5 pages
Document 3 → 2 pages
Document 4 → 4 pages

Total ≈ 14 pages
```

An LLM cannot efficiently process all of this because:

* Context windows are limited.
* Larger prompts increase cost.
* More irrelevant text distracts the model.
* Noise increases hallucination risk.

The compression module removes unnecessary information while preserving information relevant to the query.

---

## What does it actually do?

It **does not summarize the whole document**.

Instead, it extracts only the pieces related to the question.

Suppose the user asks:

> "How does self-attention work?"

Retrieved document:

```text
Transformer Architecture

History...
Motivation...
Encoder...
Decoder...
Applications...
Self Attention
Formula
Examples
Training
Future Work
References
```

Compression outputs:

```text
Self Attention

Definition

Formula

Scaled Dot Product

Multi Head Attention

Advantages
```

Everything else is discarded.

---

## How is compression implemented?

There are several techniques.

---

### Technique 1: Extractive Compression

Keep only relevant paragraphs.

```text
Original

20 paragraphs

↓

Select

Paragraph 5

Paragraph 9

Paragraph 12
```

No rewriting occurs.

Only selection.

---

### Technique 2: LLM Compression

Prompt the LLM:

```text
Extract only information
relevant to the user's query.
```

Example

Input

```text
10 pages
```

Output

```text
Only relevant 20 lines
```

This is the most common implementation in frameworks like LangChain's `ContextualCompressionRetriever`.

---

### Technique 3: Embedding-based Filtering

Compute similarity between:

```
Query

and

Sentence
```

Remove sentences below a threshold.

```text
Similarity

Sentence 1

0.92

Keep

Sentence 2

0.18

Remove
```

---

### Technique 4: Cross-Encoder Filtering

Instead of cosine similarity,

run every sentence through a reranker.

```
Question

+

Sentence

↓

Cross Encoder

↓

Relevance Score
```

Keep only the highest scores.

---

## Final output

```text
Retrieved Documents

↓

Compression

↓

Relevant Context Only
```

---

# 2. Prompt Builder

## Why does it exist?

LLMs do not consume "documents."

They consume a **prompt**.

The prompt builder constructs the final prompt by combining:

* system instructions
* user question
* retrieved context
* metadata
* citations
* formatting rules

---

Without a prompt builder

The LLM receives

```text
Question

Documents
```

With a prompt builder

```text
You are an AI assistant.

Answer ONLY using the context.

If insufficient information,
say you don't know.

Context:

...

Question:

...

Answer:
```

---

## What components does it build?

A production prompt often looks like

```text
SYSTEM

You are an expert assistant.

------------

INSTRUCTIONS

Use only retrieved context.

------------

RETRIEVED DOCUMENTS

Document 1

Document 2

Document 3

------------

USER QUESTION

...

------------

OUTPUT FORMAT

Markdown

------------

ANSWER
```

The prompt builder assembles all of this automatically.

---

## Advanced prompt builders

Modern systems also add

### Metadata

```text
Source

Wikipedia

Confidence

0.91

Document ID

123
```

---

### Citations

```text
[1]

Transformer Paper

[2]

Attention is All You Need
```

---

### Few-shot examples

```text
Example Question

Example Answer
```

---

### Conversation history

```text
Previous Question

...

Previous Answer

...
```

---

Everything is merged before the LLM call.

---

# 3. LLM Generation Module

This is the easiest module to understand.

Its job is simply:

```
Prompt

↓

LLM

↓

Answer
```

However, internally, much more happens.

---

## Input

The model receives

```text
System Prompt

Instructions

Retrieved Context

Question

Conversation History

Examples
```

---

## Tokenization

The prompt becomes

```text
Token IDs
```

---

## Transformer Forward Pass

The model performs

```
Embedding

↓

Attention

↓

Feed Forward

↓

Attention

↓

...

↓

Prediction
```

This repeats for every generated token.

---

## Autoregressive Generation

The LLM predicts

```
Next Token

↓

Append

↓

Predict Again

↓

Append
```

Until

* EOS token
* maximum length
* stop sequence

---

## Decoding

The model may use

* Greedy decoding
* Beam Search
* Top-k sampling
* Top-p sampling
* Temperature

depending on configuration.

---

Output

```text
Final Answer
```

---

# 4. Verification Module

This is probably the least understood module.

Many people think generation is the last step.

In production,

it often is not.

Large companies frequently verify answers before showing them.

---

## Why verify?

LLMs can

* hallucinate
* misquote
* invent citations
* contradict retrieved documents
* answer unsupported questions

Verification catches these problems.

---

## What does verification check?

Several aspects can be evaluated.

---

### A. Groundedness (Faithfulness)

Does the answer actually come from the retrieved context?

Example

Retrieved

```text
Transformer introduced in 2017.
```

Generated

```text
Transformer introduced in 2016.
```

Verification

```text
Unsupported

Reject
```

---

### B. Citation Verification

Suppose the model says

```
According to Document 3...
```

Verify

```
Is this statement
actually present
inside Document 3?
```

---

### C. Hallucination Detection

Answer

```
The model has 12 billion parameters.
```

Documents

```
No parameter count mentioned.
```

Verification

```
Hallucination

Reject
```

---

### D. Consistency

Check for contradictions.

Example

```
Paragraph 1

Accuracy 94%

Paragraph 3

Accuracy 89%
```

Verifier detects inconsistency.

---

### E. Completeness

Did the answer address all parts of the question?

Question

```
Compare GPT and BERT
```

Answer

```
Only GPT
```

Verifier

```
Incomplete
```

---

## How is verification implemented?

Several techniques exist.

---

### Technique 1: LLM-as-a-Judge

Prompt another LLM:

```text
Question

Context

Answer

Evaluate:

Faithfulness

Completeness

Correctness
```

The verifier returns a score or structured judgment.

---

### Technique 2: NLI (Natural Language Inference)

Treat

Retrieved context

as the premise

Answer

as the hypothesis

Predict

```
Entailment

Contradiction

Neutral
```

If the answer is not entailed by the context, it may be rejected.

---

### Technique 3: Retrieval-Based Verification

Retrieve again using the generated answer.

If new evidence contradicts the answer,

flag it.

---

### Technique 4: Rule-Based Verification

Simple deterministic checks such as

* required citation format
* JSON validity
* schema validation
* forbidden claims

---

## What happens after verification?

If verification passes:

```text
Answer

↓

User
```

If verification fails, different recovery strategies are possible.

### Option 1

Retrieve more context.

```text
Verification Failed

↓

Retrieve Again
```

---

### Option 2

Regenerate.

```text
Verification Failed

↓

LLM Again
```

---

### Option 3

Escalate.

```text
"I don't have enough evidence
to answer confidently."
```

---

# Complete Flow

```text
Retriever
     │
     ▼
Retrieved Documents
     │
     ▼
Compression
(Remove irrelevant content)
     │
     ▼
Compressed Context
     │
     ▼
Prompt Builder
(Construct the final LLM prompt)
     │
     ▼
LLM Generation
(Produce an answer from the prompt)
     │
     ▼
Verification
(Check grounding, correctness, citations, consistency)
     │
     ├───────────────┐
     │               │
     ▼               ▼
Pass            Fail
     │               │
     ▼               ▼
Return Answer   Regenerate / Retrieve More / Reject
```

## How these modules complement one another

Each module addresses a different problem:

| Module             | Primary Purpose                                                                             | Typical Techniques                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Compression**    | Reduce irrelevant retrieved content while preserving query-relevant information             | Extractive filtering, contextual compression, embedding similarity, cross-encoder filtering, LLM extraction |
| **Prompt Builder** | Convert retrieved knowledge and instructions into a structured prompt optimized for the LLM | Prompt templates, context formatting, citation insertion, conversation history, few-shot examples           |
| **LLM Generation** | Reason over the prompt and generate the final response                                      | Transformer inference with autoregressive decoding (greedy, beam, top-k, top-p, etc.)                       |
| **Verification**   | Ensure the generated answer is supported, consistent, and complete before returning it      | LLM-as-a-judge, NLI models, retrieval-based validation, rule-based checks                                   |

Together, these modules separate concerns: **compression** improves signal-to-noise ratio, **prompt building** presents information in the most effective form, **generation** produces the answer, and **verification** acts as a quality-control gate before the response reaches the user.


## Key Takeaway

The most important insight from the Modular RAG paper is that **it is not another retrieval algorithm**. It is an **architectural framework** for constructing RAG systems from **independent, composable modules** connected by orchestration operators such as **routing, branching, fusion, scheduling, and looping**. The paper's contribution is to provide a unifying abstraction that can represent many existing RAG techniques—Hybrid RAG, GraphRAG, Agentic RAG, Adaptive RAG, and others—as different compositions of reusable modules rather than isolated architectures. This makes Modular RAG a blueprint for building flexible, maintainable, and production-ready RAG systems rather than a single new retrieval method. ([arXiv][1])

[1]: https://arxiv.org/abs/2407.21059?utm_source=chatgpt.com "Modular RAG: Transforming RAG Systems into LEGO-like Reconfigurable Frameworks"
