# Cahier des charges (HelloFmap)

## 1. Titre
**HelloFmap — Plateforme d’onboarding digital multi‑département (MVP)**

## 2. Introduction
**Objectif général :** Fournir un prototype fonctionnel permettant de centraliser et d’automatiser l’intégration des nouveaux employés (documents, checklists, gestion des rôles) pour une démonstration en soutenance.

## 3. Contexte et parties prenantes
**Contexte :** L’onboarding d’un nouvel employé implique plusieurs acteurs (RH, managers, responsables de département). HelloFmap vise à réduire les tâches manuelles et la dispersion d’informations.

**Parties prenantes :**
- Commanditaire / Jury : validation finale et critères de soutenance.
- Utilisateurs : SUPERADMIN, RH, Responsable DEPT, MANAGER, EMPLOYÉ.
- Développeur : porteur unique du projet (étudiant).
- Services externes optionnels : service d’envoi d’emails (pour réinitialisation mot de passe), hébergement pour démonstration.

**Responsabilités :**
- Commanditaire : valider le périmètre et la recette.
- Développeur : conception, réalisation, tests, documentation et démonstration.
- Utilisateurs (testeurs) : participer à la recette si nécessaire.

## 4. Objectifs fonctionnels (exigences)
### Fonctions essentielles (MVP) — livrables minimaux
1. **Authentification & gestion des rôles** — connexion et accès différenciés.
2. **Gestion des utilisateurs** — création, consultation, modification, suppression (avec règles d’accès selon rôle).
3. **Gestion des départements** — création et affectation d’utilisateurs.
4. **Gestion des documents** — ajout, consultation, téléchargement avec contrôle d’accès selon rôle/département.
5. **Checklists & templates** — création de templates globaux et départementaux, items et complétion.
6. **Assignation automatique d’onboarding** — génération d’items/checklists pertinents à l’affectation d’un utilisateur.
7. **Forgot / Reset password** — demande de réinitialisation et lien de reset (envoi email ou affichage en console en dev).

### Fonctions souhaitables (si le temps le permet)
- Recherche et filtres avancés sur utilisateurs et documents.
- Notifications d’assignation par e‑mail.
- UI enrichie (prévisualisation PDF, drag & drop pour upload).

### Fonctions secondaires (optionnelles)
- Migration du stockage vers un cloud (S3/GCS).
- Audit détaillé et historique des actions.
- Multilingue.

## 5. Priorisation
- **Haute (obligatoire)** : fonctionnalités essentielles listées ci‑dessus.
- **Moyenne** : fonctionnalités souhaitables.
- **Basse** : fonctionnalités secondaires.

## 6. Contraintes (non techniques)
- Projet individuel — périmètre ajusté au temps disponible.
- Prototype démontrable localement lors de la soutenance.
- Respecter la confidentialité (ne pas utiliser de données personnelles réelles sensibles dans la démonstration).
- Documentation et guide d’installation obligatoires pour la soutenance.

## 7. Livrables
- Prototype complet (backend + frontend) exécutable localement.
- Code source (dépôt Git) avec README d’installation.
- Exemple de jeu de données ou script d’initialisation pour la démo.
- Modèle de données simplifié (schéma) et guide d’utilisation.
- Rapport technique (CdC + Spécifications) et slides de présentation.

## 8. Validation — Critères de réussite
- Authentification fonctionnelle (obtenir token / accès protégé).
- CRUD utilisateurs et départements selon règles de permission.
- Upload / download de documents vérifiables dans le dossier de stockage.
- Création et assignation de checklists ; complétion d’items par l’utilisateur.
- Flow reset password fonctionnel (lien visible en dev) et réinitialisation effective.

## 9. Procédure de recette (méthode d’acceptation)
1. Installer et démarrer l’application (instructions dans README).
2. Créer un SUPERADMIN (bootstrap ou via endpoint initial).
3. Tester le parcours complet : création utilisateur → affectation département → upload document → assignation checklist → complétion item.
4. Vérifier les règles d’accès par rôle (ex. DEPT ne voit que documents de son département + documents globaux).
5. Exécuter les tests unitaires fournis et consulter les résultats.

---