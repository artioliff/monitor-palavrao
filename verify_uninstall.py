#!/usr/bin/env python3
"""Lê a senha de stdin e imprime SENHA_OK, SENHA_ERRADA ou CONFIG_NAO_ENCONTRADO."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("SENHA_ERRADA", file=sys.stderr)
        sys.exit(2)
    dest = Path(sys.argv[1])
    cfg_path = dest / "config.json"
    if not cfg_path.exists():
        print("CONFIG_NAO_ENCONTRADO")
        return
    senha = sys.stdin.readline().rstrip("\r\n")
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    h = hashlib.sha256(senha.encode("utf-8")).hexdigest()
    print("SENHA_OK" if h == cfg.get("senha_hash", "") else "SENHA_ERRADA")


if __name__ == "__main__":
    main()
