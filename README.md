# API Blog — INF222 TAF1

API REST backend pour gérer un blog simple.

## Installation
```bash
pip3 install flask flask-mysqldb flask-jwt-extended
```

## Lancer le serveur
```bash
python3 app.py
```

## Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | /auth/register | Inscription |
| POST | /auth/login | Connexion (retourne un token JWT) |
| GET | /api/articles | Liste tous les articles |
| GET | /api/articles/{id} | Un article par ID |
| POST | /api/articles | Créer un article (JWT requis) |
| PUT | /api/articles/{id} | Modifier un article (JWT requis) |
| DELETE | /api/articles/{id} | Supprimer un article (JWT requis) |
| GET | /api/articles/search?query=texte | Rechercher un article |

## Auteur
SOH PAGUI PASCAL RUMMEL — 24G2720 — UY1 Informatique L2
