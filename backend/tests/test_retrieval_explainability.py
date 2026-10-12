import re

import numpy as np
import pytest

from app.mlops.retrieval_explainability import _query_terms


def test_query_terms_preserve_identifiers_and_deduplicate_case_insensitively():
    assert _query_terms("Refund refund PaymentService payment_service") == [
        "Refund", "PaymentService", "payment_service"
    ]


def test_query_terms_respect_maximum_feature_count():
    query = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi"
    assert len(_query_terms(query, maximum=6)) == 6


class FakeEmbedder:
    vocabulary = ["where", "refund", "service", "validates", "payment", "amount", "limit", "invoice"]

    def _vector(self, text):
        words = re.findall(r"[a-z]+", text.lower())
        vector = np.array([sum(1 for word in words if word == token) for token in self.vocabulary], dtype=float)
        norm = np.linalg.norm(vector)
        return vector / norm if norm else vector

    def embed_text(self, text):
        return self._vector(text).tolist()

    def embed_texts(self, texts):
        return [self._vector(text).tolist() for text in texts]


def test_shap_lime_explain_bge_similarity_for_a_candidate_when_installed():
    pytest.importorskip("shap")
    pytest.importorskip("lime")
    from app.mlops.retrieval_explainability import explain_query_code_similarity

    result = explain_query_code_similarity(
        query="where refund service validates payment amount",
        candidate={
            "content": "refund service validates payment amount limit",
            "file_path": "backend/app/services/refund_service.py",
            "symbol_name": "refund_service.validate_refund",
            "start_line": 10,
            "end_line": 35,
            "score": 0.82,
        },
        embedder=FakeEmbedder(),
        num_samples=30,
    )

    assert result["explanation_target"] == "BGE-M3 query-to-code cosine similarity"
    assert result["does_not_explain_llm_reasoning"] is True
    assert result["shap"] and result["lime"]
    assert all("term" in row and "contribution" in row for row in result["shap"])
    assert all("term" in row and "contribution" in row for row in result["lime"])
