# Monitor Parental (Monitor Palavrão)

Monitora fala capturada do microfone; ao detectar palavrões acima do limite configurado, emite avisos e pode **desligar o PC**.

## Avisos importantes

- O desligamento é **forçado** (`shutdown /s /f /t 0`). Use com cuidado para evitar perda de trabalho.
- Requer microfone funcional e permissões de captura.

## Dependências

- Python 3 no Windows
- Pacotes em `requirements.txt`
- `pyaudio` pode exigir instalação adicional no Windows

## Instalar (Windows)

1. Clique com o botão direito em `instalar.bat` → **Executar como administrador**
2. O instalador copia os scripts para `%ProgramData%\MonitorParental` e cria tarefas no Agendador:
   - `MonitorParental` (ONLOGON)
   - `MonitorParentalWatchdog` (a cada 5 minutos)

### Se aparecer `cho` em vez de `echo`, `et` em vez de `net`, ou `´╗┐@echo`

O **CMD** é sensível ao encoding dos `.bat`:

- **UTF-8 com BOM** pode aparecer como lixo (`´╗┐`) na primeira linha e quebrar o script.
- **UTF-8 sem BOM** pode fazer o CMD “comer” o primeiro caractere de cada linha.

**Solução usada neste projeto:** `instalar.bat` e `desinstalar.bat` ficam em **Unicode UTF-16 LE com BOM** (formato nativo no Windows). Se você editar esses arquivos no editor e eles voltarem a UTF-8, rode na pasta do projeto:

`powershell -ExecutionPolicy Bypass -File .\encode_bat_utf16.ps1`

Isso regrava os dois `.bat` em UTF-16 LE. Alternativa: no Notepad, *Salvar como* → codificação **Unicode**.

### Se aparecer “Python não foi encontrado” (Microsoft Store)

O Windows pode redirecionar `python.exe` para a loja. Desative os aliases:

**Configurações → Aplicativos → Aliases de execução do aplicativo** → desligue **python.exe** e **python3.exe**.

O instalador tenta usar antes o launcher **`py`** (normalmente vem com o Python oficial) e caminhos típicos em `%LocalAppData%\Programs\Python\`.

### Senha mestre

- A senha mestre usada para parar/desinstalar é: **JesusEstáVendo**
- A senha não é salva em texto puro; é armazenada como hash em `%ProgramData%\MonitorParental\config.json`.

## Desinstalar (Windows)

1. Clique com o botão direito em `desinstalar.bat` → **Executar como administrador**
2. Informe a senha mestre quando solicitado

## Logs

- `%ProgramData%\MonitorParental\monitor.log`
- `%ProgramData%\MonitorParental\watchdog.log`
