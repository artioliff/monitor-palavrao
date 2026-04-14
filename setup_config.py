#!/usr/bin/env python3
"""Grava config.json com hash da senha (stdin, --b64 ou --default-password)."""
from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

# Senha mestre padrao (mesma regra do instalador antigo)
_DEFAULT_PASSWORD = "JesusEstáVendo"


def main() -> None:
    if len(sys.argv) < 3:
        print(
            "Uso: setup_config.py <pasta_destino> <avisos_int> [--default-password | --b64 BASE64]",
            file=sys.stderr,
        )
        sys.exit(2)
    dest = Path(sys.argv[1])
    avisos = int(sys.argv[2])
    if len(sys.argv) >= 4 and sys.argv[3] == "--default-password":
        senha = _DEFAULT_PASSWORD
    elif len(sys.argv) >= 5 and sys.argv[3] == "--b64":
        senha = base64.b64decode(sys.argv[4]).decode("utf-8")
    else:
        senha = sys.stdin.readline().rstrip("\r\n")
    dest.mkdir(parents=True, exist_ok=True)
    cfg = {
        "senha_hash": hashlib.sha256(senha.encode("utf-8")).hexdigest(),
        "avisos": avisos,
        "idioma": "pt-BR",
    }
    with open(dest / "config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print("Config salvo.")


if __name__ == "__main__":
    main()
