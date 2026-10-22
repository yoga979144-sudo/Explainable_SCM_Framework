from models import db
from models.database_models import OrganizationalMemory, ActivityLog
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_all_memories(category=None, outcome=None, search=None):
    query = OrganizationalMemory.query
    if category and category != 'All':
        query = query.filter(OrganizationalMemory.category == category)
    if outcome and outcome != 'All':
        query = query.filter(OrganizationalMemory.implementation_outcome == outcome)
    if search:
        term = f"%{search}%"
        query = query.filter(
            (OrganizationalMemory.memory_id.ilike(term)) |
            (OrganizationalMemory.description.ilike(term)) |
            (OrganizationalMemory.change_type.ilike(term)) |
            (OrganizationalMemory.lessons_learned.ilike(term)) |
            (OrganizationalMemory.relevant_characteristics.ilike(term))
        )
    return query.order_by(OrganizationalMemory.recorded_date.desc()).all()

def get_memory_by_id(memory_id):
    return OrganizationalMemory.query.filter_by(memory_id=memory_id).first()

def get_next_memory_id():
    count = OrganizationalMemory.query.count()
    return f"MEM-{count + 1:03d}"

def add_memory_record(
    category,
    change_type,
    description,
    relevant_characteristics,
    previous_value,
    new_value,
    historical_trust_score=None,
    test_result='Passed',
    approval_outcome='Approved',
    implementation_outcome='Success',
    failure_success_details=None,
    lessons_learned=None,
    source_cr_id=None,
    project_name='Enterprise SCM Core',
    user='System'
):
    mem_id = get_next_memory_id()
    mem = OrganizationalMemory(
        memory_id=mem_id,
        project_name=project_name,
        category=category,
        change_type=change_type,
        description=description,
        relevant_characteristics=relevant_characteristics,
        previous_value=previous_value,
        new_value=new_value,
        historical_trust_score=historical_trust_score,
        test_result=test_result,
        approval_outcome=approval_outcome,
        implementation_outcome=implementation_outcome,
        failure_success_details=failure_success_details,
        lessons_learned=lessons_learned,
        source_cr_id=source_cr_id,
        recorded_date=datetime.utcnow()
    )
    db.session.add(mem)

    log = ActivityLog(
        user=user,
        action="Added Organizational Memory Record",
        module="Organizational Memory",
        details=f"Stored memory {mem_id}: {change_type} ({implementation_outcome})"
    )
    db.session.add(log)
    db.session.commit()
    return mem

def find_similar_memories(target_description, target_category, target_change_type="", limit=5):
    """
    Genuine similarity retrieval using TF-IDF cosine similarity + category alignment.
    Returns:
        List of dicts: [
           {
             'memory': OrganizationalMemory,
             'similarity_score': float (0-100),
             'match_reasons': list of str
           }
        ]
    """
    records = OrganizationalMemory.query.all()
    if not records:
        return []

    # Build corpus
    corpus = [
        f"{m.category} {m.change_type} {m.description} {m.relevant_characteristics or ''}"
        for m in records
    ]
    query_text = f"{target_category} {target_change_type} {target_description}"

    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus + [query_text])
        # Cosine similarity of query (last element) with each corpus record
        similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]
    except Exception:
        # Fallback keyword overlap if text is very short
        similarities = np.zeros(len(records))
        query_words = set(query_text.lower().split())
        for idx, doc in enumerate(corpus):
            doc_words = set(doc.lower().split())
            overlap = len(query_words.intersection(doc_words))
            similarities[idx] = overlap / max(len(query_words), 1)

    results = []
    for idx, mem in enumerate(records):
        base_sim = float(similarities[idx])
        # Category bonus
        category_match = (mem.category.lower() == target_category.lower())
        change_type_match = bool(target_change_type and mem.change_type.lower() == target_change_type.lower())
        
        sim_percentage = base_sim * 70.0
        match_reasons = []

        if category_match:
            sim_percentage += 20.0
            match_reasons.append(f"Identical CI category ({mem.category})")
        if change_type_match:
            sim_percentage += 10.0
            match_reasons.append(f"Matching change type ({mem.change_type})")
        if base_sim > 0.15:
            match_reasons.append(f"High text & characteristic alignment (TF-IDF: {base_sim:.2f})")

        sim_percentage = min(100.0, max(0.0, sim_percentage))

        # Include if similarity is meaningful (> 15%) or category matches
        if sim_percentage >= 15.0 or category_match:
            results.append({
                'memory': mem,
                'similarity_score': round(sim_percentage, 1),
                'match_reasons': match_reasons
            })

    # Sort descending by similarity score
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    return results[:limit]
