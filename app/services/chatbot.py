def answer_question(question: str, documents: list):
    # naive: return the titles of documents mentioning any word
    qwords = set(question.lower().split())
    matches = []
    for d in documents:
        text = (d.content or "") + " " + (d.title or "")
        if any(w in text.lower() for w in qwords):
            matches.append({"title": d.title, "snippet": (d.content or '')[:200]})
    return {"answer": "See related documents below.", "sources": matches}