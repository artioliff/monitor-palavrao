#!/usr/bin/env python3
"""
Watchdog — Reinicia o monitor se ele parar inesperadamente.
Executado pelo Agendador de Tarefas a cada 5 minutos.
"""
import subprocess, sys, os, time, logging
from pathlib import Path

BASE_DIR   = Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) / "MonitorParental"
LOG_FILE   = BASE_DIR / "watchdog.log"
MONITOR_PY = BASE_DIR / "monitor_completo.py"
PYTHON     = sys.executable

BASE_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  WATCHDOG  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")],
)

def monitor_rodando() -> bool:
    """Verifica se monitor_completo.py está em execução."""
    try:
        if not MONITOR_PY.exists():
            return False

        ps = r"""
$ErrorActionPreference = 'SilentlyContinue'
$target = [Regex]::Escape($args[0])
$p = Get-CimInstance Win32_Process |
  Where-Object { $_.Name -in @('python.exe','pythonw.exe') -and $_.CommandLine -match $target } |
  Select-Object -First 1 -ExpandProperty ProcessId
if ($p) { Write-Output $p }
"""
        saida = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", ps, str(MONITOR_PY)],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return bool(saida)
    except Exception:
        return False

def iniciar_monitor():
    pythonw = Path(PYTHON).parent / "pythonw.exe"
    if not pythonw.exists():
        pythonw = PYTHON  # fallback para python.exe
    subprocess.Popen(
        [str(pythonw), str(MONITOR_PY)],
        creationflags=0x00000008,  # DETACHED_PROCESS
        close_fds=True,
    )
    logging.info(f"✅ Monitor reiniciado: {MONITOR_PY}")

if __name__ == "__main__":
    if not monitor_rodando():
        logging.info("⚠️ Monitor não encontrado. Reiniciando...")
        iniciar_monitor()
    else:
        logging.info("🟢 Monitor está rodando normalmente.")
