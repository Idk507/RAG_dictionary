# Faithfulness-Optimized RAG

Faithfulness-Optimized Retrieval-Augmented Generation (Faithfulness-Optimized RAG) is a class of RAG systems specifically designed to **minimize hallucinations and ensure that every generated statement is directly supported by retrieved evidence**. The primary objective is not merely to produce correct answers but to produce answers that are **faithful to the retrieved context**.

Traditional RAG assumes that supplying relevant documents is sufficient for grounding an LLM. In practice, however, an LLM may still inject unsupported facts, combine retrieved information with its parametric memory, misinterpret evidence, or fabricate details. Faithfulness-Optimized RAG introduces additional mechanisms before, during, and after generation to verify that the model's output remains anchored to the retrieved evidence.

---

# What Does "Faithfulness" Mean?

Faithfulness measures whether the generated answer is completely supported by the retrieved documents.

Suppose the retrieved document contains:

```
The Eiffel Tower was completed in 1889.
```

A faithful answer is:

```
The Eiffel Tower was completed in 1889.
```

An unfaithful answer might be:

```
The Eiffel Tower was completed in 1889 and became the tallest building in Europe until 1930.
```

Even if the added statement is historically true, it is **not faithful** unless the retrieved context explicitly supports it.

Thus, faithfulness is about **grounding**, not general correctness.

---

# Objective of Faithfulness-Optimized RAG

Instead of optimizing only answer quality,

Traditional RAG aims to maximize:

<img width="121" height="40" alt="image" src="https://github.com/user-attachments/assets/dd09834e-1432-45f9-9a11-00f15cd3a2c5" />

where:

* (Q): query
* (D): retrieved documents
* (A): generated answer

Faithfulness-Optimized RAG instead seeks to maximize:

<img width="276" height="33" alt="image" src="https://github.com/user-attachments/assets/b7e95fe8-91ae-4b11-8484-7b6303f7a0b8" />


The emphasis shifts from generating plausible answers to generating **evidence-supported answers**.

---

# Overall Workflow

```text
               User Query
                    │
                    ▼
            Retrieve Documents
                    │
                    ▼
          Rerank / Filter Evidence
                    │
                    ▼
       Evidence Sufficiency Check
                    │
          ┌─────────┴─────────┐
          │                   │
   Enough Evidence?         No
          │                  │
          ▼                  ▼
    Generate Answer     Retrieve Again
          │
          ▼
 Statement-Level Verification
          │
          ▼
 Unsupported Claims?
          │
     ┌────┴────┐
     │         │
    Yes       No
     │         │
     ▼         ▼
 Revise     Final Answer
```

The distinguishing feature is that **generation is followed by verification**, and unsupported claims trigger revision rather than immediate delivery.

---

# Why Traditional RAG Still Hallucinates

Even with high-quality retrieval, several failure modes remain:

1. The retriever misses important evidence.
2. The LLM combines retrieved facts with memorized knowledge.
3. The model makes unsupported inferences.
4. The model overgeneralizes beyond the evidence.
5. Retrieved documents contain conflicting information.

Faithfulness optimization addresses these issues by explicitly checking whether the answer is grounded.

---

# Mathematical Formulation

Let:

* (Q): query
* (D = {d_1, d_2, ..., d_k}): retrieved documents
* (A): generated answer

<img width="625" height="440" alt="image" src="https://github.com/user-attachments/assets/08c43468-8665-4c5f-a9a6-22d36b6e35b4" />

---

# Step 1 — High-Quality Retrieval

Faithfulness begins with reliable evidence retrieval.

Typical strategies include:

* Hybrid retrieval (dense + sparse)
* Cross-encoder reranking
* Query expansion
* Multi-query retrieval
* Knowledge graph retrieval
* Parent document retrieval

The goal is to maximize **evidence recall**, ensuring that all facts needed to answer the question are available.

---

# Step 2 — Evidence Filtering

Not all retrieved documents contribute equally.

Suppose ten documents are retrieved:

```
D1
D2
...
D10
```

A reranker assigns relevance scores:

[
r_i
]

The highest-scoring evidence forms:

[
D^*
]

Only this filtered evidence is passed to the generator, reducing noise and opportunities for hallucination.

---

# Step 3 — Evidence Sufficiency

Before generation, the system estimates whether the retrieved evidence is sufficient.

Define:

[
S(D,Q)
]

where:

* (S=1): sufficient evidence
* (S=0): insufficient evidence

If the evidence is inadequate, the system may:

* retrieve more documents,
* rewrite the query,
* switch retrievers,
* search external sources,
* or ask the user for clarification.

This prevents the model from answering questions that lack adequate support.

---

# Step 4 — Grounded Generation

Instead of prompting the model simply with:

```
Answer the question.
```

the instruction becomes more restrictive:

```
Use only the provided documents.
Do not introduce outside knowledge.
If the evidence is insufficient, say so.
```

The decoding objective is effectively constrained to remain within the retrieved evidence.

---

# Step 5 — Statement-Level Decomposition

After generation, the answer is decomposed into individual factual claims.

Example:

```
Apple was founded in 1976.
Steve Jobs was CEO until 2011.
Apple invented the smartphone.
```

These become:

```
Claim 1
Claim 2
Claim 3
```

Each claim is independently verified against the retrieved evidence.

---

# Step 6 — Claim Verification

For each claim (c_i), the system evaluates:

<img width="192" height="37" alt="image" src="https://github.com/user-attachments/assets/8494baaa-adc1-4ada-8068-36c2e8c1c24a" />


This is analogous to a Natural Language Inference (NLI) problem.

Possible outcomes:

* **Entailed**: the evidence supports the claim.
* **Contradicted**: the evidence refutes the claim.
* **Not supported**: the evidence neither confirms nor denies it.

Only entailed claims are retained.

---

# Natural Language Inference (NLI)

Many faithfulness pipelines use NLI models.

Input:

```
Evidence:
Apple was founded in 1976.
```

Claim:

```
Apple started in 1976.
```

Output:

```
Entailment
```

Another claim:

```
Apple was founded in 1980.
```

Output:

```
Contradiction
```

Another claim:

```
Apple created Linux.
```

Output:

```
Not supported
```

This enables automated verification of generated statements.

---

# Step 7 — Attribution

Each accepted statement is linked back to its supporting evidence.

Example:

```
Apple was founded in 1976.
(Source: Document 3)
```

This explicit attribution improves traceability and user trust.

---

# Step 8 — Faithfulness Score

Suppose an answer contains (n) claims.

Let:

* (m): supported claims

The faithfulness score is:

<img width="102" height="83" alt="image" src="https://github.com/user-attachments/assets/0dabc272-c8e6-402b-8220-5e4f63cd23e4" />


Example:

```
8 supported claims
2 unsupported claims
```
<img width="482" height="182" alt="image" src="https://github.com/user-attachments/assets/7c217d11-d217-4ca5-9212-9e47244f49ca" />


before accepting an answer.

---

# Step 9 — Self-Correction

If unsupported claims are detected, the system revises the answer.

Loop:

```text
Generate
    │
    ▼
Verify
    │
Unsupported?
    │
 ┌──┴──┐
 │     │
Yes    No
 │      │
 ▼      ▼
Revise  Finalize
```

This iterative refinement improves grounding.

---

# Faithfulness Metrics

Several metrics are commonly used to quantify faithfulness:

| Metric               | Description                                                              |
| -------------------- | ------------------------------------------------------------------------ |
| Claim Support Rate   | Fraction of claims supported by evidence                                 |
| Citation Precision   | Percentage of citations that genuinely support the associated statements |
| Attribution Accuracy | Correct mapping between claims and source passages                       |
| Hallucination Rate   | Fraction of unsupported or fabricated statements                         |
| NLI Entailment Score | Probability that generated claims are entailed by the evidence           |
| Context Utilization  | Degree to which retrieved evidence is actually used during generation    |

---

# Common Architectural Components

A Faithfulness-Optimized RAG system often combines multiple modules:

| Component          | Role                                             |
| ------------------ | ------------------------------------------------ |
| Retriever          | Finds potentially relevant evidence              |
| Reranker           | Prioritizes the most relevant documents          |
| Evidence Filter    | Removes noisy or redundant passages              |
| Generator          | Produces an answer constrained by the evidence   |
| Claim Extractor    | Splits the answer into atomic factual statements |
| NLI Verifier       | Determines whether each claim is supported       |
| Citation Generator | Links claims to supporting passages              |
| Revision Module    | Removes or rewrites unsupported claims           |

---

# Research Techniques

Current research explores several complementary approaches:

### 1. Constrained Decoding

The decoder is biased toward tokens supported by retrieved evidence, reducing the likelihood of introducing unsupported facts.

### 2. Retrieval-Augmented Verification

A separate verifier checks the generated output against the retrieved context before the answer is returned.

### 3. Self-Verification

The LLM critiques its own answer by comparing each statement with the evidence and revising unsupported content.

### 4. Citation-Guided Generation

The model is trained or prompted to generate answers alongside supporting citations, encouraging stronger grounding.

### 5. Retrieval Refinement

If verification fails because evidence is incomplete, the system retrieves additional documents and regenerates the answer.

---

# Advantages

Faithfulness-Optimized RAG provides several important benefits:

* Significantly reduces hallucinations by grounding responses in retrieved evidence.
* Improves transparency through explicit citations and traceable reasoning.
* Produces answers that are easier to audit and verify.
* Is particularly valuable in high-stakes domains such as healthcare, law, finance, scientific literature, and enterprise knowledge management.
* Supports automated quality assurance through claim-level verification.

---

# Limitations

Despite its strengths, this approach has trade-offs:

* Verification introduces additional computational cost and latency.
* NLI and verification models are not perfect and may incorrectly classify claims.
* If retrieval misses critical evidence, even a faithful system may conclude that the answer is unsupported.
* Strict faithfulness can reduce completeness, since the model avoids including correct information that is absent from the retrieved context.
* Claim extraction and attribution become more difficult for long, complex, or highly inferential responses.

---

# Faithfulness-Optimized RAG vs Traditional RAG

| Aspect                     | Traditional RAG           | Faithfulness-Optimized RAG           |
| -------------------------- | ------------------------- | ------------------------------------ |
| Primary objective          | Generate accurate answers | Generate evidence-supported answers  |
| Hallucination control      | Limited                   | Explicit verification and revision   |
| Grounding                  | Implicit                  | Explicit and measurable              |
| Statement verification     | Not typically performed   | Claim-by-claim verification          |
| Citations                  | Optional                  | Often mandatory                      |
| Evidence sufficiency check | Rare                      | Common                               |
| Post-generation validation | Usually absent            | Standard component                   |
| Typical applications       | General QA                | High-assurance and regulated domains |

# Research Perspective

Faithfulness-Optimized RAG can be viewed as extending classical Retrieval-Augmented Generation with an additional optimization objective: **maximize evidence alignment rather than answer plausibility**. From a probabilistic perspective, the system seeks to maximize both the likelihood of the answer given the query and evidence, (P(A \mid Q, D)), and the probability that every factual claim in the answer is entailed by the retrieved documents. This places Faithfulness-Optimized RAG at the intersection of **retrieval**, **natural language inference**, **factual consistency evaluation**, and **iterative self-correction**.

Rather than treating retrieval as the final grounding step, the retrieved evidence becomes a continuously evaluated constraint throughout the pipeline. Modern implementations therefore combine retrieval, reranking, evidence sufficiency estimation, claim decomposition, NLI-based verification, citation generation, and answer revision into a closed-loop architecture whose primary goal is to ensure that every output statement can be traced back to explicit supporting evidence. This makes Faithfulness-Optimized RAG one of the most reliable architectures for applications where explainability, auditability, and factual grounding are as important as answer quality itself.
