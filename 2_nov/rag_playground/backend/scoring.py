"""Score one model answer: keyword accuracy plus embedding-based relevance and groundedness.

- correct:      every keyword group has at least one match (a keyword must start at a word boundary,
                so "6" does not match inside "16", but "tuesday" matches "Tuesdays").
- relevance:    cosine similarity of question vs answer (0-1).
- groundedness: highest cosine similarity of answer vs any retrieved chunk (0-1).

Relevance and groundedness are None for refusals and empty answers: a refusal is judged by
keyword accuracy alone, and its similarity to the question or chunks says nothing useful.
"""
import re

from rag_common import get_embedder

REFUSAL_PHRASES = ["cannot find", "can't find", "not in the provided"]


def _normalize(text):
    return text.replace("’", "'").lower()


def _contains(text, keyword):
    return re.search(r"\b" + re.escape(keyword.lower()), text) is not None


def keyword_match(answer, keyword_groups):
    """Return (correct, matched, missing): matched keywords, and the groups that had no match."""
    text = _normalize(answer)
    matched, missing = [], []
    for group in keyword_groups:
        hit = next((kw for kw in group if _contains(text, kw)), None)
        if hit:
            matched.append(hit)
        else:
            missing.append(group)
    return not missing, matched, missing


def is_refusal(answer):
    text = _normalize(answer)
    return any(_contains(text, p) for p in REFUSAL_PHRASES)


def _similarities(answer, others):
    """Cosine similarity of `answer` against each text in `others`, clipped to 0-1."""
    vectors = get_embedder().encode([answer] + others, normalize_embeddings=True)
    return [max(0.0, float(vectors[0] @ v)) for v in vectors[1:]]


def score_answer(item, answer, hits):
    """Score one answer to an eval item (from eval/questions.json) given the chunks the model saw."""
    correct, matched, missing = keyword_match(answer, item["keywords"])
    relevance = groundedness = None
    if answer.strip() and not is_refusal(answer):
        sims = _similarities(answer, [item["question"]] + [h["text"] for h in hits])
        relevance = sims[0]
        groundedness = max(sims[1:], default=None)
    return {
        "correct": correct,
        "matched": matched,
        "missing": missing,
        "relevance": relevance,
        "groundedness": groundedness,
    }
