"""
NLP-based Knowledge Graph Extraction (No LLM Calls)
===================================================
This module provides alternatives to LLM-based entity extraction
using local NLP models: spaCy, transformers, or co-occurrence.

Advantages:
- Zero LLM API costs
- Much faster (5-10ms vs 200-500ms per chunk)
- Offline-capable
- Scales to millions of chunks

Tradeoffs:
- May miss complex semantic relationships
- Less nuanced entity descriptions
- Works best for factual/named entity tasks
"""

import spacy
from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict, Counter
import re
import logging

logger = logging.getLogger("nlp_graph_extraction")


# ===========================================================================
# OPTION 1: SpaCy NER + Dependency Parsing (Best Quality)
# ===========================================================================

class SpacyGraphExtractor:
    """Extract entities and relationships using spaCy NER and dependency parsing.
    
    Installation:
        pip install spacy
        python -m spacy download en_core_web_lg  # 780MB, best accuracy
        # OR
        python -m spacy download en_core_web_sm  # 12MB, faster but less accurate
    
    Performance: ~10-20ms per chunk on CPU
    """
    
    def __init__(self, model_name: str = "en_core_web_lg"):
        """
        Args:
            model_name: 'en_core_web_sm' (fast), 'en_core_web_md' (balanced), 
                       'en_core_web_lg' (accurate), 'en_core_web_trf' (transformer-based, best)
        """
        self.nlp = spacy.load(model_name)
        logger.info(f"Loaded spaCy model: {model_name}")
    
    def extract_entities_and_relationships(self, text: str, max_entities: int = 20) -> Dict[str, Any]:
        """Extract entities and relationships from text using spaCy.
        
        Returns same format as LLM-based extraction for drop-in replacement.
        """
        doc = self.nlp(text)
        
        # Extract entities with spaCy NER
        entities = []
        entity_set = set()
        
        for ent in doc.ents[:max_entities]:
            if ent.text.strip() and len(ent.text) > 2:  # Filter short/empty
                # Map spaCy types to our schema
                entity_type = self._map_entity_type(ent.label_)
                
                # Get entity context for description
                description = self._get_entity_context(ent, doc)
                
                entities.append({
                    "name": ent.text.strip(),
                    "type": entity_type,
                    "description": description
                })
                entity_set.add(ent.text.strip())
        
        # Extract relationships using dependency parsing
        relationships = self._extract_relationships_from_dependencies(doc, entity_set)
        
        return {
            "entities": entities,
            "relationships": relationships
        }
    
    def _map_entity_type(self, spacy_label: str) -> str:
        """Map spaCy entity labels to our schema."""
        mapping = {
            "PERSON": "person",
            "ORG": "organization",
            "GPE": "location",      # Geopolitical entity
            "LOC": "location",
            "EVENT": "event",
            "PRODUCT": "object",
            "WORK_OF_ART": "object",
            "LAW": "concept",
            "LANGUAGE": "concept",
            "NORP": "organization",  # Nationalities, religious/political groups
            "FAC": "location",       # Facilities
            "DATE": "event",
            "TIME": "event",
            "MONEY": "object",
            "QUANTITY": "object",
            "ORDINAL": "object",
            "CARDINAL": "object"
        }
        return mapping.get(spacy_label, "concept")
    
    def _get_entity_context(self, entity, doc, window: int = 5) -> str:
        """Get surrounding context for entity description."""
        # Find sentence containing entity
        sent = entity.sent
        # Get a few words around the entity
        start = max(0, entity.start - window)
        end = min(len(sent), entity.end + window)
        context = doc[start:end].text.strip()
        return context[:200]  # Limit description length
    
    def _extract_relationships_from_dependencies(self, doc, entity_set: Set[str]) -> List[Dict[str, str]]:
        """Extract relationships using dependency parsing.
        
        Looks for patterns like:
        - Entity1 [verb] Entity2
        - Entity1 is [description] of Entity2
        """
        relationships = []
        
        # Find entity spans
        entity_spans = {ent.text.strip(): ent for ent in doc.ents if ent.text.strip() in entity_set}
        
        # Extract verb-based relationships
        for token in doc:
            if token.pos_ == "VERB":
                # Find subject and object
                subjects = [child.text for child in token.children if child.dep_ in ("nsubj", "nsubjpass")]
                objects = [child.text for child in token.children if child.dep_ in ("dobj", "pobj", "attr")]
                
                for subj in subjects:
                    for obj in objects:
                        # Check if subject and object are entities
                        if subj in entity_set and obj in entity_set and subj != obj:
                            relationships.append({
                                "source": subj,
                                "target": obj,
                                "relation": token.lemma_,  # Base form of verb
                                "description": f"{subj} {token.text} {obj}"
                            })
        
        return relationships


# ===========================================================================
# OPTION 2: Hugging Face Transformers NER (Good Balance)
# ===========================================================================

class TransformersGraphExtractor:
    """Extract entities using Hugging Face transformers NER models.
    
    Installation:
        pip install transformers torch
    
    Models:
        - dslim/bert-base-NER (fast, 110M params)
        - dslim/bert-large-NER (better, 340M params)
        - Babelscape/wikineural-multilingual-ner (multilingual)
    
    Performance: ~30-50ms per chunk on CPU, ~5ms on GPU
    """
    
    def __init__(self, model_name: str = "dslim/bert-base-NER"):
        from transformers import pipeline
        self.ner_pipeline = pipeline("ner", model=model_name, aggregation_strategy="simple")
        logger.info(f"Loaded Hugging Face NER model: {model_name}")
    
    def extract_entities_and_relationships(self, text: str, max_entities: int = 20) -> Dict[str, Any]:
        """Extract entities using transformers NER."""
        # Run NER
        ner_results = self.ner_pipeline(text)
        
        # Convert to our format
        entities = []
        entity_names = set()
        
        for ent in ner_results[:max_entities]:
            if ent['score'] > 0.5:  # Confidence threshold
                entity_type = self._map_entity_type(ent['entity_group'])
                entities.append({
                    "name": ent['word'].strip(),
                    "type": entity_type,
                    "description": f"Confidence: {ent['score']:.2f}"
                })
                entity_names.add(ent['word'].strip())
        
        # Extract co-occurrence relationships
        relationships = self._extract_cooccurrence_relationships(text, entity_names)
        
        return {
            "entities": entities,
            "relationships": relationships
        }
    
    def _map_entity_type(self, hf_label: str) -> str:
        """Map Hugging Face NER labels to our schema."""
        mapping = {
            "PER": "person",
            "ORG": "organization",
            "LOC": "location",
            "MISC": "concept"
        }
        return mapping.get(hf_label, "concept")
    
    def _extract_cooccurrence_relationships(self, text: str, entities: Set[str]) -> List[Dict[str, str]]:
        """Extract relationships based on co-occurrence in sentences."""
        relationships = []
        sentences = text.split('.')
        
        for sent in sentences:
            # Find which entities appear in this sentence
            entities_in_sent = [e for e in entities if e in sent]
            
            # Create relationships for co-occurring entities
            if len(entities_in_sent) >= 2:
                for i, e1 in enumerate(entities_in_sent):
                    for e2 in entities_in_sent[i+1:]:
                        relationships.append({
                            "source": e1,
                            "target": e2,
                            "relation": "co-occurs",
                            "description": f"Mentioned together in: {sent[:100]}..."
                        })
        
        return relationships


# ===========================================================================
# OPTION 3: Co-occurrence + Pattern Matching (Fastest, No Dependencies)
# ===========================================================================

class CooccurrenceGraphExtractor:
    """Extract entities and relationships using co-occurrence and patterns.
    
    No external dependencies required (uses regex).
    
    Advantages:
        - Extremely fast (~1-2ms per chunk)
        - No model downloads
        - Works offline immediately
    
    Tradeoffs:
        - Lower quality than NER models
        - May extract non-entities (proper nouns only)
        - Simple co-occurrence relationships
    
    Best for: Quick prototyping, very large datasets, simple domains
    """
    
    def __init__(self):
        logger.info("Initialized co-occurrence graph extractor (no models required)")
    
    def extract_entities_and_relationships(self, text: str, max_entities: int = 20) -> Dict[str, Any]:
        """Extract entities using regex patterns for proper nouns."""
        # Extract capitalized phrases (likely entities)
        entity_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        entity_candidates = re.findall(entity_pattern, text)
        
        # Count frequency and filter common words
        entity_counts = Counter(entity_candidates)
        stopwords = {'The', 'A', 'An', 'This', 'That', 'These', 'Those', 'What', 'When', 'Where', 'Who', 'Why', 'How'}
        
        entities = []
        entity_names = set()
        
        for entity, count in entity_counts.most_common(max_entities):
            if entity not in stopwords and len(entity) > 2:
                # Guess entity type based on hints
                entity_type = self._guess_entity_type(entity, text)
                
                entities.append({
                    "name": entity,
                    "type": entity_type,
                    "description": f"Mentioned {count} time(s)"
                })
                entity_names.add(entity)
        
        # Extract co-occurrence relationships
        relationships = self._extract_cooccurrence(text, entity_names)
        
        return {
            "entities": entities,
            "relationships": relationships
        }
    
    def _guess_entity_type(self, entity: str, text: str) -> str:
        """Guess entity type based on context clues."""
        # Simple heuristics
        if ' ' not in entity:
            # Single word - likely person or organization
            context = text.lower()
            if any(word in context for word in ['mr.', 'mrs.', 'dr.', 'said', 'told']):
                return "person"
            elif any(word in context for word in ['company', 'corporation', 'inc', 'ltd']):
                return "organization"
        else:
            # Multi-word - could be location or organization
            if any(word in entity.lower() for word in ['city', 'country', 'state', 'street']):
                return "location"
        
        return "concept"
    
    def _extract_cooccurrence(self, text: str, entities: Set[str], window: int = 100) -> List[Dict[str, str]]:
        """Extract relationships based on proximity within text window."""
        relationships = []
        
        # Sliding window approach
        for i, entity1 in enumerate(entities):
            pos1 = text.find(entity1)
            if pos1 == -1:
                continue
            
            for entity2 in list(entities)[i+1:]:
                pos2 = text.find(entity2, pos1)
                
                # If entities appear within window, create relationship
                if 0 < pos2 - pos1 < window * len(entity1):
                    snippet = text[pos1:pos2+len(entity2)]
                    relationships.append({
                        "source": entity1,
                        "target": entity2,
                        "relation": "related_to",
                        "description": snippet[:100]
                    })
        
        return relationships


# ===========================================================================
# HYBRID APPROACH: NER + LLM for Summaries Only
# ===========================================================================

class HybridGraphExtractor:
    """Use local NER for entity extraction, LLM only for community summaries.
    
    Best of both worlds:
        - Fast, free entity extraction (local NER)
        - High-quality summaries (LLM, but only C calls for C communities)
        - Reduces LLM calls from N chunks to C communities (typically 5-20)
    
    Example: 1000 chunks → 1000 NER calls (local) + 10 LLM calls (summaries)
             vs original: 1000 LLM calls + 10 LLM calls
    
    Cost reduction: ~99% for entity extraction
    """
    
    def __init__(self, extractor_type: str = "spacy"):
        """
        Args:
            extractor_type: 'spacy', 'transformers', or 'cooccurrence'
        """
        if extractor_type == "spacy":
            self.extractor = SpacyGraphExtractor()
        elif extractor_type == "transformers":
            self.extractor = TransformersGraphExtractor()
        else:
            self.extractor = CooccurrenceGraphExtractor()
        
        logger.info(f"Hybrid approach: {extractor_type} for entities, LLM for summaries only")
    
    def extract_entities_and_relationships(self, text: str, max_entities: int = 20) -> Dict[str, Any]:
        """Extract using local NER (no LLM call)."""
        return self.extractor.extract_entities_and_relationships(text, max_entities)


# ===========================================================================
# COMPARISON TABLE
# ===========================================================================

"""
Method Comparison:

┌─────────────────────┬─────────────┬──────────────┬─────────────┬─────────────────┐
│ Method              │ LLM Calls   │ Speed/Chunk  │ Quality     │ Best For        │
├─────────────────────┼─────────────┼──────────────┼─────────────┼─────────────────┤
│ Original (LLM)      │ N chunks    │ 200-500ms    │ ⭐⭐⭐⭐⭐ │ Complex docs    │
│ SpaCy NER           │ 0           │ 10-20ms      │ ⭐⭐⭐⭐   │ Factual text    │
│ Transformers NER    │ 0           │ 30-50ms      │ ⭐⭐⭐⭐   │ Modern NLP      │
│ Co-occurrence       │ 0           │ 1-2ms        │ ⭐⭐⭐     │ Large scale     │
│ Hybrid (NER+LLM)    │ C communities│ 10ms + few  │ ⭐⭐⭐⭐   │ Best balance    │
└─────────────────────┴─────────────┴──────────────┴─────────────┴─────────────────┘

Cost Comparison (1000 chunks):
- Original: 1000 LLM calls × $0.0001 = $0.10 (entity extraction) + summaries
- SpaCy: $0 (local) + summaries
- Hybrid: $0 (local) + ~10 summary calls = $0.001

Speed Comparison (1000 chunks):
- Original: 1000 × 300ms = 5 minutes
- SpaCy: 1000 × 15ms = 15 seconds
- Co-occurrence: 1000 × 2ms = 2 seconds

Recommendation:
1. **Production**: Use Hybrid approach (SpaCy + LLM summaries)
2. **Prototyping**: Use Co-occurrence (fastest, simplest)
3. **Research papers**: Use original LLM (best quality)
4. **Multilingual**: Use transformers with multilingual model
"""
