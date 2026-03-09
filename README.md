# Bot Discord - Chat Événement

Bot de mini-événements automatiques : le plus rapide à taper le mot affiché dans une image gagne 1 point.

## Fonctionnalités

- **Événements automatiques** toutes les 20 minutes
- **Images générées** avec un mot au centre (style fond étoilé)
- **Système de points** : 1 point par victoire
- **Rôles récompenses** :
  - 5 victoires → Rôle 1
  - 10 victoires → Rôle 2
  - 20 victoires → Rôle 3
  - 50 victoires → Rôle 4

## Installation

1. **Python 3.8+** requis

2. **Installer les dépendances** :
   ```
   pip install -r requirements.txt
   ```

3. **Configurer** le fichier `config.json` :
   - `token` : Ton token de bot Discord (https://discord.com/developers/applications)
   - `channel_id` : L'ID du salon où les événements auront lieu
   - `roles` : Les IDs des 4 rôles (5_wins, 10_wins, 20_wins, 50_wins)
   - `interval_minutes` : Intervalle entre chaque événement (défaut: 20)
   - `words_file` : Fichier contenant les mots (un par ligne)

4. **Créer les rôles** sur ton serveur, activer le mode développeur sur Discord, clic droit sur chaque rôle → Copier l'identifiant.

5. **Permissions du bot** : Vérifier que le bot peut lire/envoyer des messages et gérer les rôles.

## Lancement

```
python bot.py
```

## Commandes

- `!points [@utilisateur]` - Affiche le nombre de victoires
- `!classement` - Top 10 des joueurs

## Structure des fichiers

- `bot.py` - Bot principal
- `image_generator.py` - Génération des images
- `database.py` - Gestion des scores
- `words.txt` - Liste des mots pour les événements
- `config.json` - Configuration
- `data/` - Scores et images temporaires
