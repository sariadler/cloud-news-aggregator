from transformers import pipeline
from backend.models.schemas import CATEGORIES

# הטעינה הראשונה יכולה לקחת זמן – תקין
_zero_shot = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")
_ner = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
 
def classify_topic(text: str):
    res = _zero_shot(text, CATEGORIES)
    label = res["labels"][0]
    score = float(res["scores"][0])
    return label, score


# פונקציה שמחלצת ישויות מטקסט
def extract_entities(text: str, max_chars: int = 800):
    ents = _ner(text[:max_chars])
    out = []
    for e in ents:
        w = e.get("word") or e.get("entity_group") or ""
        if w: out.append(w)
    return out
