from app.crud.checklist_crud import (
    create_checklist_item,
    list_department_template,
    list_checklist_items_for_user,
    delete_checklist_item
)
from app.crud.document_crud import list_documents

def assign_onboarding_for_user(db, user):
    """
    Assigne les checklist items et documents à un utilisateur en fonction de son département.
    - Supprime les items liés à l'ancien département qui ne sont plus valides
    - Ne crée pas de doublons
    - Met à jour le department_id des items existants si nécessaire
    - Ajoute seulement les items manquants selon le département actuel
    """
    # Templates globaux + départementaux
    global_templates = list_department_template(db, department_id=None)
    dept_templates = list_department_template(db, department_id=user.department_id) if user.department_id else []

    templates = global_templates + dept_templates
    template_titles = {t.title: t for t in templates}

    # Récupère les items existants pour l'utilisateur
    existing_items = list_checklist_items_for_user(db, user.id)
    created_or_updated = []

    for item in existing_items:
        # Supprimer les items liés à un ancien département qui ne sont plus dans les templates
        if item.department_id is not None and item.title not in template_titles:
            delete_checklist_item(db, item.id)
        else:
            # Mise à jour du department_id si nécessaire
            if item.title in template_titles and item.department_id != template_titles[item.title].department_id:
                item.department_id = template_titles[item.title].department_id
                db.commit()
                db.refresh(item)
            created_or_updated.append(item)

    # Ajouter les items manquants
    existing_titles = {item.title for item in created_or_updated}
    for t in templates:
        if t.title not in existing_titles:
            new_item = create_checklist_item(db, type('X', (), {
                'title': t.title,
                'department_id': t.department_id,
                'user_id': user.id
            })())
            created_or_updated.append(new_item)

    # Récupère documents du département actuel
    docs = list_documents(db, department_id=user.department_id)

    return created_or_updated, docs
