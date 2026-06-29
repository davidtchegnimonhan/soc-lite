"""
Gestion du statut de suivi des alertes (Nouvelle / Vue / Résolue)
Stockage simple en fichier JSON (pas de dépendance externe)
"""

import json
import os
import hashlib
import threading

STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alert_statuses.json')
VALID_STATUSES = ['new', 'reviewed', 'resolved']

_lock = threading.Lock()


def make_alert_id(ip, first_seen):
    """Génère un identifiant stable et court pour une alerte (IP + première occurrence)"""
    raw = f"{ip}|{first_seen}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]


def _load():
    if not os.path.exists(STATUS_FILE):
        return {}
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save(data):
    with open(STATUS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_status(alert_id):
    """Retourne le statut d'une alerte, 'new' par défaut si jamais enregistrée"""
    with _lock:
        data = _load()
        return data.get(alert_id, 'new')


def get_all_statuses():
    """Retourne tous les statuts enregistrés (dict alert_id -> status)"""
    with _lock:
        return _load()


def set_status(alert_id, status):
    """Enregistre le statut d'une alerte. Retourne False si statut invalide."""
    if status not in VALID_STATUSES:
        return False
    with _lock:
        data = _load()
        data[alert_id] = status
        _save(data)
    return True
