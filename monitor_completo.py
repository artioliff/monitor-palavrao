#!/usr/bin/env python3
"""
Monitor Parental — Versão Protegida
Roda na bandeja do sistema. Requer senha para parar.
"""

import threading, time, os, sys, queue, logging, subprocess, platform
import tkinter as tk
from tkinter import simpledialog, messagebox
from pathlib import Path

from monitor_lib import (
    PALAVROES,
    check_profanity,
    get_base_dir,
    load_config,
    save_config,
    verify_password,
)

try:
    import speech_recognition as sr
except ImportError:  # permite importar o módulo para testes unitários
    sr = None

# ──────────────────────────────────────────
#  CAMINHOS
# ──────────────────────────────────────────
BASE_DIR = get_base_dir()
CONFIG_FILE = BASE_DIR / "config.json"
LOG_FILE    = BASE_DIR / "monitor.log"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────
#  LOGGING
# ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ──────────────────────────────────────────
#  CONFIGURAÇÃO
# ──────────────────────────────────────────
def carregar_config():
    return load_config(CONFIG_FILE)


def salvar_config(cfg):
    return save_config(CONFIG_FILE, cfg)


def verificar_senha(senha: str) -> bool:
    return verify_password(senha, carregar_config())

# ──────────────────────────────────────────
#  PALAVRÕES
# ──────────────────────────────────────────
# Exemplo de expansão organizada por "radical"
def checar_palavrao(texto: str):
    return check_profanity(texto, PALAVROES)

# ──────────────────────────────────────────
#  DESLIGAR
# ──────────────────────────────────────────
def desligar_pc():
    logging.warning("🔴 DESLIGANDO O COMPUTADOR!")
    if platform.system() == "Windows":
        os.system("shutdown /s /f /t 0")
    else:
        os.system("sudo shutdown -h now")

def beep():
    try:
        import winsound
        for _ in range(4):
            winsound.Beep(1000, 250)
            time.sleep(0.1)
    except Exception:
        print("\a\a\a\a")

# ──────────────────────────────────────────
#  MONITOR DE VOZ
# ──────────────────────────────────────────
class MonitorVoz:
    def __init__(self, on_aviso, on_desligar):
        if sr is None:
            raise RuntimeError("Dependência ausente: SpeechRecognition (e/ou PyAudio). Reinstale e tente novamente.")
        self.on_aviso    = on_aviso
        self.on_desligar = on_desligar
        self.rodando     = True
        self.fila        = queue.Queue()
        self.rec         = sr.Recognizer()
        self.rec.energy_threshold         = 300
        self.rec.dynamic_energy_threshold = True
        self.rec.pause_threshold          = 0.6
        self.contador    = 0
        self.ultimo_em   = 0
        cfg = carregar_config()
        self.max_avisos  = int(cfg.get("avisos", 2))
        self.idioma      = cfg.get("idioma", "pt-BR")

    def processar_audio(self):
        while self.rodando:
            try:
                audio = self.fila.get(timeout=1)
                try:
                    texto = self.rec.recognize_google(audio, language=self.idioma)
                    logging.info(f"🎙️ '{texto}'")
                    palavrao = checar_palavrao(texto)
                    if palavrao:
                        agora = time.time()
                        if agora - self.ultimo_em < 10:
                            continue
                        self.ultimo_em = agora
                        self.contador += 1
                        logging.warning(f"🚨 Palavrão: '{palavrao}' | Aviso {self.contador}")
                        if self.contador > self.max_avisos:
                            self.on_desligar(palavrao)
                        else:
                            restam = self.max_avisos - self.contador + 1
                            self.on_aviso(palavrao, self.contador, restam)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    logging.error(f"API voz: {e}")
                    time.sleep(5)
            except queue.Empty:
                continue

    def iniciar(self):
        t = threading.Thread(target=self.processar_audio, daemon=True)
        t.start()
        self._stop_listen = None
        self._source = None
        try:
            self._source = sr.Microphone()
            with self._source as source:
                logging.info("Calibrando microfone...")
                self.rec.adjust_for_ambient_noise(source, duration=2)
            self._stop_listen = self.rec.listen_in_background(
                self._source, lambda r, a: self.fila.put(a), phrase_time_limit=10
            )
            while self.rodando:
                time.sleep(0.5)
        except OSError as e:
            logging.error(f"Microfone: {e}")

    def parar(self):
        self.rodando = False
        if self._stop_listen:
            self._stop_listen(wait_for_stop=True)

# ──────────────────────────────────────────
#  ÍCONE NA BANDEJA
# ──────────────────────────────────────────
def criar_icone_imagem(cor="green"):
    from PIL import Image, ImageDraw
    img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    fill = (34, 197, 94) if cor == "green" else (239, 68, 68)
    draw.ellipse([4, 4, 60, 60], fill=fill)
    draw.text((20, 18), "👦", fill="white")
    return img

class AplicacaoBandeja:
    def __init__(self):
        self.monitor = None
        self.icone   = None
        self.status  = "monitorando"

    def pedir_senha(self, titulo="Senha Mestre"):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        senha = simpledialog.askstring(titulo, "Digite a senha mestre:", show="*", parent=root)
        root.destroy()
        return senha

    def on_aviso(self, palavrao, num, restam):
        beep()
        logging.warning(f"⚠️ AVISO {num}: '{palavrao}' — {restam} restante(s) antes de desligar")
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

    def on_desligar(self, palavrao):
        beep()
        logging.warning(f"💥 Desligando por: '{palavrao}'")
        desligar_pc()

    def acao_parar(self, icon, item):
        senha = self.pedir_senha("Parar Monitor")
        if senha is None:
            return
        if verificar_senha(senha):
            logging.info("🔓 Monitor parado com senha correta.")
            if self.monitor:
                self.monitor.parar()
            icon.stop()
            # Desabilita a tarefa agendada
            os.system('schtasks /Change /TN "MonitorParental" /DISABLE >nul 2>&1')
            os.system('schtasks /Change /TN "MonitorParentalWatchdog" /DISABLE >nul 2>&1')
        else:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Acesso Negado", "❌ Senha incorreta!", parent=root)
            root.destroy()
            logging.warning("🔒 Tentativa de parar com senha errada!")

    def acao_status(self, icon, item):
        cfg  = carregar_config()
        avisos = cfg.get("avisos", 2)
        idioma = cfg.get("idioma", "pt-BR")
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Monitor Parental",
            f"🟢 Status: Monitorando\n"
            f"🎙️ Idioma: {idioma}\n"
            f"⚠️ Avisos antes de desligar: {avisos}\n"
            f"📋 Log em: {LOG_FILE}",
            parent=root
        )
        root.destroy()

    def iniciar(self):
        try:
            import pystray
            from PIL import Image
        except ImportError:
            logging.error("pystray/Pillow não instalado!")
            self._iniciar_sem_bandeja()
            return

        menu = pystray.Menu(
            pystray.MenuItem("🟢 Monitor Parental — Ativo", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("📊 Ver Status",        self.acao_status),
            pystray.MenuItem("🔴 Parar (senha)",     self.acao_parar),
        )

        self.icone = pystray.Icon(
            "MonitorParental",
            criar_icone_imagem("green"),
            "Monitor Parental 🟢",
            menu,
        )

        # Inicia monitor de voz em thread separada
        self.monitor = MonitorVoz(self.on_aviso, self.on_desligar)
        t = threading.Thread(target=self.monitor.iniciar, daemon=True)
        t.start()

        logging.info("🟢 Monitor iniciado com ícone na bandeja.")
        self.icone.run()

    def _iniciar_sem_bandeja(self):
        logging.info("Rodando sem bandeja (modo console).")
        self.monitor = MonitorVoz(self.on_aviso, self.on_desligar)
        self.monitor.iniciar()


if __name__ == "__main__":
    app = AplicacaoBandeja()
    app.iniciar()
