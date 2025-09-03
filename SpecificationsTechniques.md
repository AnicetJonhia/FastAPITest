

# SpecTech.md — Spécifications techniques (HelloFmap)

> Document technique décrivant **comment** réaliser HelloFmap : architecture, modèle de données, API, sécurité, tests et plan de déploiement.

## 1. Vue d'ensemble
**But :** fournir un guide technique complet permettant au développeur (ou à un futur contributeur) d’implémenter le MVP HelloFmap conforme au CdC.

## 2. Architecture générale
- **Type :** Application web client‑serveur (SPA ↔ API REST).
- **Composants :**
  - Frontend : SPA (interface utilisateur selon rôle).
  - Backend : API REST exposant les ressources métier.
  - Base de données relationnelle (fichier pour MVP).
  - Stockage fichiers (dossier local pour MVP).
  - Service d’envoi d’emails (SMTP) avec fallback console en dev.

**Diagramme logique (conceptuel) :**
```
[Frontend (navigateur)] <--HTTPS--> [Backend API] <---> [Base de données]
                                       |---> [Storage (fichiers)]
                                       |---> [SMTP / service email]
```

## 3. Choix technologiques recommandés
- Backend : Python 3.10+ avec FastAPI.
- ORM : SQLAlchemy (ou équivalent) + Alembic pour migrations (prod).
- Base : SQLite pour MVP ; PostgreSQL recommandé en production.
- Frontend : React (Vite ou CRA) + Axios pour appels API.
- Styling : Tailwind CSS (rapide) ou Bootstrap.
- Serveur dev : Uvicorn.
- Tests : pytest (backend), jest + react‑testing‑library (frontend).
- Emails : FastAPI‑Mail ou lib SMTP.

> Ces choix sont des recommandations. Ils sont détaillés ici pour guider l’implémentation.

## 4. Modélisation des données (ER simplifié)
### Entités principales
- **User**: id, email, username, hashed_password, full_name, role (SUPERADMIN|RH|DEPT|MANAGER|EMPLOYEE), department_id (nullable), is_active, created_at
- **Department**: id, name, description, created_at
- **Document**: id, title, filename_on_disk, original_filename, department_id (nullable), uploaded_by_id (FK User), uploaded_at, metadata (json)
- **ChecklistTemplate**: id, title, department_id (nullable pour global), created_by_id, created_at
- **ChecklistItem**: id, template_id (FK), title, description, order_index
- **ChecklistAssignment**: id, user_id (FK), item_id (FK ChecklistItem), status (pending|completed), assigned_at, completed_at
- **PasswordResetToken**: token, user_id, expires_at

> Indexer user.email, documents.department_id, checklist_assignments.user_id.

## 5. Endpoints API (contrat)
### Auth
- `POST /api/auth/token` — form data: `username`, `password` → `{ access_token, token_type }`
- `POST /api/auth/forgot-password` — `{ "email": "..." }` → crée token court et envoie lien (ou affiche en console).
- `POST /api/auth/reset-password` — `{ token, new_password, confirm_password }` → valide token et met à jour mot de passe.

### Users
- `GET /api/users` — list (filtres page/size/department_id)
- `POST /api/users` — create (SUPERADMIN only)
- `GET /api/users/{id}`
- `PUT /api/users/{id}`
- `DELETE /api/users/{id}`

### Departments
- `GET /api/departments`
- `POST /api/departments`
- `PUT /api/departments/{id}`
- `DELETE /api/departments/{id}`

### Documents
- `GET /api/documents` — filtres: department_id, global
- `POST /api/documents` — multipart/form-data: title, department_id?, file
- `GET /api/documents/{id}/download` — retourne le fichier (permission check)
- `PUT /api/documents/{id}` — update metadata
- `DELETE /api/documents/{id}`

### Checklists
- `POST /api/checklists/template` — create template (user_id must be null)
- `GET /api/checklists` — filtres: user_id, department_id
- `GET /api/checklists/me` — assignments for current user
- `POST /api/checklists/assign/{user_id}` — assign templates → create assignments
- `POST /api/checklists/{id}/complete` — mark assignment completed
- `PUT /api/checklists/{id}` — update item/template
- `DELETE /api/checklists/{id}`

**Réponses** : JSON standard, codes HTTP RESTful (200, 201, 400, 401, 403, 404).

## 6. Règles métiers (comportements clés)
- **Accès documents** :
  - SUPERADMIN / RH : accès à tous les documents.
  - DEPT / MANAGER : accès aux documents globaux (department_id=NULL) et aux documents de leur propre département.
- **Templates checklist** : si department_id présent → template lié au département, sinon global.
- **Assignation automatique** : création (au moment de la création d’un user ou changement de department_id) des ChecklistAssignment pour les templates applicables.
- **Modification department_id** sur un user → réévaluer les assignations (option : recréer assignations applicables et archiver anciennes).

## 7. Authentification & sécurité
- **JWT** : HS256, claim `sub` = user_id, `exp` pour expiration.
- **Hashing mots de passe** : bcrypt (ou argon2 si disponible).
- **Permissions** : vérifications côté API via dépendances (FastAPI Depends) pour exiger rôle/ownership.
- **Rate‑limit** : limiter endpoints sensibles (`/auth/token`, `/auth/forgot-password`).
- **Secrets** : stockés dans `.env` (dev) et secret manager en prod.
- **HTTPS** : exigé en production (reverse proxy).

## 8. Stockage fichiers
- **Emplacement** : `STORAGE_DIR` configurable via `.env`.
- **Organisation** : `STORAGE_DIR/YYYY/MM/{uuid}_{original_filename}`.
- **Validation** : vérifier mime type et taille max (ex. 10–50 MB selon besoin).
- **Sécurité** : empêcher l’accès direct non‑autorisé, servir fichiers via endpoint après contrôle de permission.

## 9. Tests
- **Unitaires (backend)** : pytest — auth, CRUD, assignation, permission logic.
- **Intégration** : TestClient (FastAPI) pour scénarios critiques (création user → assignation checklist → completion).
- **Frontend** : jest + react‑testing‑library pour components critiques (login, upload form).
- **Tests manuels** : script de recette (README) décrivant le scénario de démo.

## 10. Déploiement & packaging
- **Local (MVP)** : instructions d’installation (venv, pip install -r requirements.txt, uvicorn app.main:app --reload) et `npm start` pour frontend.
- **Conteneurisation** : Dockerfile pour backend et frontend, docker‑compose pour dev.
- **Production (optionnel)** : conteneurisation + reverse proxy (nginx), base de données PostgreSQL, stockage S3.
- **CI** : GitHub Actions exécutant tests et linter sur chaque push.

## 11. Observabilité & maintenance
- **Logging** : logging structuré (INFO/ERROR) et fichiers de logs.
- **Monitoring** : possibilité d’intégrer Sentry pour erreurs, Prometheus pour métriques (optionnel).
- **Backups** : procédure de sauvegarde DB et fichiers si passage en prod.

## 12. Planification (6 semaines — proposition)
- **Semaine 1** : Spécifications définitives, setup repo, modèles DB, endpoints auth/users/departments.
- **Semaine 2** : Documents (upload/download) + permissions.
- **Semaine 3** : Checklists (templates + assignation automatique).
- **Semaine 4** : Frontend minimal (login, dashboard, users, docs, checklists).
- **Semaine 5** : Tests, corrections, amélioration UI/UX.
- **Semaine 6** : Documentation, packaging, préparation de la démonstration et des slides.

## 13. Annexes utiles
- Exemple `.env.example` :
```
DATABASE_URL=sqlite:///./hellofmap.db
SECRET_KEY=super_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256
ADMIN_EMAIL=admin@futurmap.com
ADMIN_PASSWORD=admin123
STORAGE_DIR=./storage
SMTP_SERVER=smtp.ethereal.email
SMTP_PORT=587
SMTP_TLS=True
SMTP_USER=your_ethereal_user@ethereal.email
SMTP_PASSWORD=your_ethereal_password
EMAIL_FROM=your_ethereal_user@ethereal.email
FRONTEND_URL=http://localhost:3000
FORGET_PASSWORD_LINK_EXPIRE_MINUTES=60
FORGET_PASSWORD_SECRET_KEY=another_secret_for_resets
```

---



