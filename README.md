# AdSeason

Plateforme SaaS de recommandation publicitaire intelligente basée sur l'analyse saisonnière et comportementale des données e-commerce.

## Stack

| Couche | Technologie |
|--------|------------|
| Frontend | Angular 21 + SCSS |
| Backend | FastAPI + Uvicorn |
| Base de données | PostgreSQL 16 |
| ML | scikit-learn (K-means) |
| Déploiement | Vercel (front) + Render (back + DB) |

## Démarrage local

### Prérequis
- Docker Desktop
- Node.js 22+
- Python 3.12+

### 1. Base de données
```bash
docker-compose up -d
```

### 2. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```
API disponible sur http://localhost:8000  
Swagger : http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
ng serve
```
App disponible sur http://localhost:4200

## Structure du projet

```
adseason/
├── frontend/          # Angular (→ Vercel)
│   └── src/app/
│       ├── core/      # services, guards, interceptors, models
│       ├── shared/    # composants réutilisables
│       └── features/  # auth, dashboard, recommendations, history, analytics
├── backend/           # FastAPI (→ Render)
│   └── app/
│       ├── models/    # SQLAlchemy ORM
│       ├── schemas/   # Pydantic
│       ├── routers/   # endpoints API
│       ├── services/  # logique métier
│       └── ml/        # modèle K-means
├── docker-compose.yml # PostgreSQL local
└── render.yaml        # config déploiement Render
```

## Déploiement

- **Frontend** → Vercel : connecter le repo, `Root Directory = frontend`
- **Backend** → Render : connecter le repo, le `render.yaml` configure tout automatiquement
