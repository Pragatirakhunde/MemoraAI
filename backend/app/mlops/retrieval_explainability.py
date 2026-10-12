"""Model-agnostic explanations for BGE-M3 query-to-code cosine similarity.

This explains retrieval similarity, not the internal reasoning of Gemini/another LLM.
SHAP and LIME perturb query terms and observe how similarity to one authorized code chunk changes.
"""
from __future__ import annotations

import re
from typing import Any


class ExplainabilityDependenciesMissing(RuntimeError):
    pass


def _query_terms(query: str, maximum: int = 12) -> list[str]:
    raw = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|[0-9]+", query)
    terms: list[str] = []
    seen: set[str] = set()
    for token in raw:
        # Preserve original identifier spelling; dedupe case-insensitively.
        key = token.casefold()
        if key not in seen:
            seen.add(key)
            terms.append(token)
    return terms[:maximum]


def explain_query_code_similarity(
    *,
    query: str,
    candidate: dict[str, Any],
    embedder,
    num_samples: int = 60,
) -> dict[str, Any]:
    """Return local SHAP and LIME token attributions for one already-authorized candidate."""
    try:
        import numpy as np
        import shap
        from lime.lime_tabular import LimeTabularExplainer
    except ImportError as exc:
        raise ExplainabilityDependenciesMissing(
            "Install backend/requirements-mlops.txt to enable SHAP/LIME explanations."
        ) from exc

    content = str(candidate.get("content") or candidate.get("code") or "")
    if not content.strip():
        raise ValueError("The selected search result has no code content to explain.")

    terms = _query_terms(query)
    if len(terms) < 2:
        raise ValueError("The query needs at least two distinct terms for token-level explanations.")

    # BGE-M3 returns normalized embeddings, so dot product is cosine similarity.
    target_vector = np.asarray(embedder.embed_text(content[:16000]), dtype=float)
    target_norm = np.linalg.norm(target_vector)
    if not target_norm:
        raise ValueError("The selected code chunk could not be embedded.")
    target_vector = target_vector / target_norm
    feature_count = len(terms)

    def predict_masks(mask_matrix):
        masks = np.asarray(mask_matrix, dtype=float)
        if masks.ndim == 1:
            masks = masks.reshape(1, -1)
        queries = [
            " ".join(term for term, keep in zip(terms, mask) if keep >= 0.5) or " "
            for mask in masks
        ]
        similarities: list[float] = []
        # Small batches limit peak memory on a local laptop and on a small deployment.
        for offset in range(0, len(queries), 12):
            batch = queries[offset:offset + 12]
            vectors = np.asarray(embedder.embed_texts(batch), dtype=float)
            similarities.extend((vectors @ target_vector).tolist())
        return np.asarray(similarities, dtype=float)

    zero = np.zeros((1, feature_count), dtype=float)
    full = np.ones((1, feature_count), dtype=float)
    sample_count = max(30, min(int(num_samples), 100))

    # SHAP KernelExplainer works on the black-box similarity function.
    shap_explainer = shap.KernelExplainer(predict_masks, zero)
    raw_shap = shap_explainer.shap_values(
        full,
        nsamples=max(sample_count, 2 * feature_count + 10),
        l1_reg=f"num_features({feature_count})",
    )
    shap_values = np.asarray(raw_shap, dtype=float)
    if shap_values.ndim == 3:
        shap_values = shap_values[0, :, 0]
    elif shap_values.ndim == 2:
        shap_values = shap_values[0]
    else:
        shap_values = shap_values.reshape(-1)

    # LIME independently fits a local linear approximation near the full query.
    training_rows = np.vstack((zero, np.eye(feature_count), full))
    lime_explainer = LimeTabularExplainer(
        training_data=training_rows,
        feature_names=terms,
        mode="regression",
        discretize_continuous=False,
        random_state=23,
    )
    lime_result = lime_explainer.explain_instance(
        full[0],
        predict_masks,
        num_features=feature_count,
        num_samples=sample_count,
    )
    lime_map_data = lime_result.as_map()
    # LIME versions may store regression explanations under label 1 or 0.
    chosen_lime_rows = lime_map_data.get(1) or lime_map_data.get(0)
    if chosen_lime_rows is None and lime_map_data:
        chosen_lime_rows = next(iter(lime_map_data.values()))
    lime_map = {int(feature_idx): float(weight) for feature_idx, weight in (chosen_lime_rows or [])}

    shap_rows = [
        {"term": term, "contribution": round(float(value), 6)}
        for term, value in zip(terms, shap_values)
    ]
    lime_rows = [
        {"term": terms[idx], "contribution": round(lime_map.get(idx, 0.0), 6)}
        for idx in range(feature_count)
    ]
    shap_rows.sort(key=lambda row: abs(row["contribution"]), reverse=True)
    lime_rows.sort(key=lambda row: abs(row["contribution"]), reverse=True)

    return {
        "explanation_target": "BGE-M3 query-to-code cosine similarity",
        "does_not_explain_llm_reasoning": True,
        "query": query,
        "candidate": {
            "file_path": candidate.get("file_path"),
            "symbol_name": candidate.get("symbol_name"),
            "start_line": candidate.get("start_line"),
            "end_line": candidate.get("end_line"),
            "qdrant_score": round(float(candidate.get("score", 0.0)), 6),
        },
        "recomputed_cosine_similarity": round(float(predict_masks(full)[0]), 6),
        "shap": shap_rows,
        "lime": lime_rows,
        "interpretation": {
            "positive": "Keeping this term increased the model similarity score in the local explanation.",
            "negative": "Keeping this term decreased the model similarity score in the local explanation.",
            "caveat": "Token attributions are local approximations of embedding similarity, not causal claims and not an explanation of generated AI prose.",
        },
        "samples": sample_count,
    }
