from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


def get_base_dir() -> Path:
    return Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) / "MonitorParental"


def load_config(path: Path) -> dict[str, Any]:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(path: Path, cfg: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, cfg: dict[str, Any]) -> bool:
    return hash_password(password) == cfg.get("senha_hash", "")


PALAVROES: dict[str, list[str]] = {
    "p_rra": ["porra", "p0rra", "prra", "purra"],
    "c_ralho": ["caralho", "carai", "krai", "c4r4lh0", "ctz", "caralhao"],
    "p_ta": ["puta", "puto", "p0ta", "putaria", "putinha", "putid"],
    "f_dp": ["fdp", "filho da puta", "filho da p", "fi da puta", "f d p"],
    "m_rda": ["merda", "m3rd4", "merdao", "merdinha"],
    "f_der": ["foder", "fuder", "foda", "fodase", "fodace", "vtnc", "vtf"],
    "b_ceta": ["buceta", "bceta", "xereca", "xota", "bucetuda"],
    "o_fensas": [
        "arrombado",
        "cuzao",
        "escroto",
        "babaca",
        "imbecil",
        "idiota",
        "otario",
        "corno",
        "verme",
    ],
}


def check_profanity(text: str, palavras: dict[str, list[str]] = PALAVROES) -> str | None:
    t = (text or "").lower()
    for _, variacoes in palavras.items():
        for v in variacoes:
            if v in t:
                return v
    return None

