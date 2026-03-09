"""
Gestion des points et des victoires des utilisateurs.
Supporte MongoDB (Railway) via MONGO_URL ou fallback JSON local.
"""
import json
import os
from pathlib import Path

DB_PATH = Path("data/scores.json")
MONGO_URL = os.environ.get("MONGO_URL")

# Client MongoDB (lazy init)
_mongo_client = None
_scores_collection = None


def _get_mongo_collection():
    """Retourne la collection MongoDB des scores."""
    global _mongo_client, _scores_collection
    if not MONGO_URL:
        return None
    if _scores_collection is None:
        from pymongo import MongoClient
        _mongo_client = MongoClient(MONGO_URL)
        db = _mongo_client.get_default_database()
        _scores_collection = db["scores"]
    return _scores_collection


def load_scores() -> dict:
    """Charge les scores depuis MongoDB ou le fichier JSON."""
    coll = _get_mongo_collection()
    if coll is not None:
        docs = list(coll.find({}, {"_id": 0}))
        return {str(d["user_id"]): {"username": d["username"], "wins": d["wins"]} for d in docs}
    # Fallback JSON
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_scores(scores: dict) -> None:
    """Sauvegarde les scores dans MongoDB ou le fichier JSON."""
    coll = _get_mongo_collection()
    if coll is not None:
        coll.delete_many({})
        if scores:
            coll.insert_many([
                {"user_id": int(uid), "username": data["username"], "wins": data["wins"]}
                for uid, data in scores.items()
            ])
        return
    # Fallback JSON
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)


def add_win(user_id: int, username: str) -> int:
    """Ajoute une victoire à l'utilisateur. Retourne le nouveau total."""
    coll = _get_mongo_collection()
    if coll is not None:
        from pymongo.collection import ReturnDocument
        result = coll.find_one_and_update(
            {"user_id": user_id},
            {"$inc": {"wins": 1}, "$set": {"username": username}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return result["wins"]
    # Fallback JSON
    scores = load_scores()
    uid = str(user_id)
    if uid not in scores:
        scores[uid] = {"username": username, "wins": 0}
    scores[uid]["wins"] += 1
    scores[uid]["username"] = username
    save_scores(scores)
    return scores[uid]["wins"]


def get_wins(user_id: int) -> int:
    """Retourne le nombre de victoires d'un utilisateur."""
    coll = _get_mongo_collection()
    if coll is not None:
        doc = coll.find_one({"user_id": user_id})
        return doc["wins"] if doc else 0
    scores = load_scores()
    uid = str(user_id)
    return scores.get(uid, {}).get("wins", 0)


def get_leaderboard(limit: int = 10) -> list:
    """Retourne le classement des meilleurs joueurs."""
    coll = _get_mongo_collection()
    if coll is not None:
        cursor = coll.find({}).sort("wins", -1).limit(limit)
        return [(d["user_id"], d["username"], d["wins"]) for d in cursor]
    scores = load_scores()
    items = [(int(uid), data["username"], data["wins"]) for uid, data in scores.items()]
    items.sort(key=lambda x: x[2], reverse=True)
    return items[:limit]
