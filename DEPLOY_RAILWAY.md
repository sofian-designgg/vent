# Déploiement sur Railway

Ce guide explique comment déployer le bot Discord sur Railway avec la base de données MongoDB.

## 1. Créer le dépôt Git

Ouvre un terminal dans le dossier du projet et exécute :

```powershell
cd c:\Users\larab\Desktop\vent

git init
git add .
git commit -m "Bot prêt pour Railway"
```

Puis crée un dépôt sur GitHub :

1. Va sur [github.com](https://github.com) → **New repository**
2. Nomme-le (ex. `vent-discord-bot`)
3. Ne coche pas "Initialize with README" (le repo existe déjà)
4. Clique sur **Create repository**
5. Connecte ton dépôt local :

```powershell
git remote add origin https://github.com/TON_USERNAME/vent-discord-bot.git
git branch -M main
git push -u origin main
```

*(Remplace `TON_USERNAME` et `vent-discord-bot` par tes valeurs.)*

---

## 2. Configurer Railway

1. Va sur [railway.app](https://railway.app) et connecte-toi (avec GitHub).
2. Clique sur **New Project** → **Deploy from GitHub repo**.
3. Choisis ton dépôt `vent-discord-bot` (ou le nom que tu as utilisé).
4. Railway va créer un service et le déployer.

---

## 3. Ajouter MongoDB

1. Dans ton projet Railway, clique sur **+ New**.
2. Choisis **Database** → **MongoDB**.
3. Attends que MongoDB soit créé. Railway ajoute automatiquement `MONGO_URL` aux variables d’environnement de ton projet.

---

## 4. Variables d’environnement

1. Clique sur ton **service bot** (celui qui affiche `bot.py`).
2. Va dans l’onglet **Variables**.
3. Ajoute ou modifie :

| Variable        | Valeur                                   | Obligatoire |
|-----------------|-------------------------------------------|-------------|
| `DISCORD_TOKEN` | Le token du bot Discord                   | Oui         |
| `CHANNEL_ID`    | L’ID du salon Discord (ex. 1234567890)   | Oui         |
| `MONGO_URL`     | Fourni automatiquement si tu as ajouté MongoDB | Oui  |

4. Clique sur **Add variable** pour chaque variable.
5. `MONGO_URL` doit déjà être là si tu as ajouté MongoDB au projet. Sinon, va dans MongoDB → **Variables** et copie `MONGO_URL`, puis colle-le dans les variables du service bot.

---

## 5. Démarrer le bot

1. Railway détecte le **Procfile** et démarre le worker avec `python bot.py`.
2. Après un nouveau déploiement, le bot redémarre automatiquement.
3. Vérifie les logs : **Deployments** → sélectionne le dernier déploiement → **View Logs**.

---

## 6. Rôles (optionnel)

Pour les rôles de victoires (5, 10, 20, 50), tu peux soit :
- garder un `config.json` dans le repo (sans le token), soit
- ajouter des variables d’environnement si le bot les supporte.

Le bot fonctionne sans rôles : les victoires sont quand même enregistrées.

---

## Commandes terminal récap

```powershell
# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Bot prêt pour Railway"

# Lier au dépôt GitHub
git remote add origin https://github.com/TON_USERNAME/vent-discord-bot.git

# Pousser sur GitHub
git push -u origin main
```

Après chaque modification :

```powershell
git add .
git commit -m "Description des changements"
git push
```

Railway redéploiera automatiquement à chaque `git push`.
