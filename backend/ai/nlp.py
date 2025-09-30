from transformers import pipeline
from backend.models.schemas import CATEGORIES

# הטעינה הראשונה יכולה לקחת זמן – תקין
_zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
_ner = pipeline("ner", grouped_entities=True)

def classify_topic(text: str) -> str:
    res = _zero_shot(text, CATEGORIES)
    return res["labels"][0] if isinstance(res, dict) and res.get("labels") else CATEGORIES[0]

def extract_entities(text: str, max_chars: int = 800):
    ents = _ner(text[:max_chars])
    out = []
    for e in ents:
        w = e.get("word") or e.get("entity_group") or ""
        if w: out.append(w)
    return out
