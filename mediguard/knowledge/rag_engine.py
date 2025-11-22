"""
Medical RAG (Retrieval-Augmented Generation) Engine
Retrieves relevant medical references and documents.
"""

import json
import os
from typing import List, Dict, Any, Optional


class MedicalRAGEngine:
    """
    Retrieves relevant medical knowledge and citations.
    In production, this would connect to a vector database with medical literature.
    """

    def __init__(self):
        """Initialize RAG engine with medical knowledge base."""
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Load medical knowledge base.
        Maps disease categories to relevant references.
        """
        # In production, this would be a vector database with embeddings
        return {
            "sepsis": [
                {
                    "title": "Surviving Sepsis Campaign Guidelines",
                    "section": "Biomarker-Guided Diagnosis",
                    "content": "Procalcitonin (PCT) levels >2.0 ng/mL are highly suggestive of bacterial sepsis. Lactate >4 mmol/L indicates severe sepsis with tissue hypoperfusion.",
                    "citation": "Rhodes A, et al. Intensive Care Med. 2017;43(3):304-377",
                },
                {
                    "title": "Sepsis-3 Consensus Definitions",
                    "section": "Diagnostic Criteria",
                    "content": "Sepsis is defined as life-threatening organ dysfunction caused by dysregulated host response to infection. SOFA score ≥2 with suspected infection.",
                    "citation": "Singer M, et al. JAMA. 2016;315(8):801-810",
                },
            ],
            "cardiac_event": [
                {
                    "title": "Fourth Universal Definition of Myocardial Infarction",
                    "section": "Troponin in Acute MI",
                    "content": "Cardiac troponin I >0.04 ng/mL indicates myocardial injury. Serial troponin rise/fall pattern diagnostic for acute MI.",
                    "citation": "Thygesen K, et al. Circulation. 2018;138(20):e618-e651",
                },
                {
                    "title": "Heart Failure Biomarkers",
                    "section": "BNP and NT-proBNP",
                    "content": "BNP >400 pg/mL suggests acute decompensated heart failure. Elevated BNP correlates with left ventricular dysfunction severity.",
                    "citation": "Januzzi JL, et al. J Am Coll Cardiol. 2019;73(9):1086-1099",
                },
            ],
            "renal_failure": [
                {
                    "title": "KDIGO Acute Kidney Injury Guidelines",
                    "section": "AKI Diagnosis",
                    "content": "AKI is defined by serum creatinine increase ≥0.3 mg/dL within 48h or ≥1.5× baseline within 7 days. Creatinine >2.0 mg/dL with rising trend indicates significant renal impairment.",
                    "citation": "KDIGO AKI Work Group. Kidney Int Suppl. 2012;2(1):1-138",
                },
            ],
            "liver_disease": [
                {
                    "title": "Acute Liver Failure Diagnosis",
                    "section": "Laboratory Markers",
                    "content": "ALT/AST >200 U/L with hyperbilirubinemia (>2.0 mg/dL) and coagulopathy (INR >1.5) suggests acute hepatocellular injury.",
                    "citation": "European Association for Study of Liver. J Hepatol. 2017;66(5):1047-1081",
                },
            ],
            "metabolic_disorder": [
                {
                    "title": "Diabetic Emergencies",
                    "section": "Hyperglycemia and DKA",
                    "content": "Blood glucose >200 mg/dL with symptoms warrants immediate evaluation. Glucose <60 mg/dL is hypoglycemia requiring urgent treatment.",
                    "citation": "American Diabetes Association. Diabetes Care. 2020;43(Suppl 1):S66-S76",
                },
                {
                    "title": "Electrolyte Disturbances",
                    "section": "Hyponatremia",
                    "content": "Serum sodium <135 mEq/L is hyponatremia. Severe hyponatremia (<125 mEq/L) requires urgent correction to prevent neurological complications.",
                    "citation": "Spasovski G, et al. Eur J Endocrinol. 2014;170(3):G1-G47",
                },
            ],
            "coagulopathy": [
                {
                    "title": "Coagulation Disorders in Critical Care",
                    "section": "DIC and Thrombosis",
                    "content": "INR >2.0 with platelet count <100×10³/μL and elevated D-dimer (>2.0 μg/mL) suggests disseminated intravascular coagulation (DIC).",
                    "citation": "Levi M, et al. N Engl J Med. 2019;381(23):2230-2241",
                },
            ],
            "anemia": [
                {
                    "title": "Anemia Classification and Management",
                    "section": "Severe Anemia",
                    "content": "Hemoglobin <10.0 g/dL is moderate anemia. Hemoglobin <7.0 g/dL is severe anemia requiring transfusion consideration.",
                    "citation": "WHO. Haemoglobin concentrations for the diagnosis of anaemia. 2011",
                },
            ],
            "infection": [
                {
                    "title": "Inflammatory Markers in Infection",
                    "section": "CRP and ESR",
                    "content": "CRP >10 mg/L suggests active inflammation. CRP >100 mg/L with elevated WBC (>11×10³/μL) indicates severe bacterial infection.",
                    "citation": "Póvoa P. Crit Care. 2002;6(5):396-399",
                },
            ],
            "normal": [
                {
                    "title": "Reference Ranges in Clinical Chemistry",
                    "section": "Normal Biomarker Ranges",
                    "content": "All measured biomarkers fall within established reference ranges for healthy adults.",
                    "citation": "Kratz A, et al. N Engl J Med. 2004;351(15):1548-1563",
                },
            ],
        }

    def retrieve_references(
        self,
        disease_category: str,
        max_results: int = 3
    ) -> List[Dict[str, str]]:
        """
        Retrieve relevant medical references for a disease category.

        Args:
            disease_category: Disease category ID
            max_results: Maximum number of references to return

        Returns:
            List of reference dicts with title, section, content, citation
        """
        if disease_category not in self.knowledge_base:
            return []

        refs = self.knowledge_base[disease_category]
        return refs[:max_results]

    def query(self, query_text: str) -> List[Dict[str, str]]:
        """
        Query knowledge base with natural language.
        Simple keyword matching; in production would use semantic search.

        Args:
            query_text: Natural language query

        Returns:
            List of relevant references
        """
        query_lower = query_text.lower()
        results = []

        # Simple keyword matching across all categories
        for category, refs in self.knowledge_base.items():
            for ref in refs:
                # Check if query keywords appear in reference
                content_lower = (
                    ref["title"] + " " +
                    ref["section"] + " " +
                    ref["content"]
                ).lower()

                if any(word in content_lower for word in query_lower.split()):
                    results.append(ref)

        # Remove duplicates and limit results
        seen = set()
        unique_results = []
        for ref in results:
            key = ref["title"] + ref["section"]
            if key not in seen:
                seen.add(key)
                unique_results.append(ref)

        return unique_results[:5]

    def format_references(self, references: List[Dict[str, str]]) -> str:
        """
        Format references for WhatsApp display.

        Args:
            references: List of reference dicts

        Returns:
            Formatted string for WhatsApp
        """
        if not references:
            return "No specific references available."

        formatted = "*📚 Medical References:*\n\n"

        for i, ref in enumerate(references, 1):
            formatted += f"{i}. *{ref['title']}* — {ref['section']}\n"
            formatted += f"   {ref['content'][:200]}{'...' if len(ref['content']) > 200 else ''}\n"
            formatted += f"   _Citation: {ref['citation']}_\n\n"

        return formatted.rstrip()
