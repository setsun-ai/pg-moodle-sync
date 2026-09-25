# Uruchamianie: ręcznie, automatycznie albo 24/7

🇬🇧 [English version](../en/running.md) · [← README](../../README.pl.md)

| Sposób | Dla kogo | Kiedy działa |
|---|---|---|
| [Ręcznie](#ręcznie) | na próbę, od czasu do czasu | gdy klikniesz |
| [Automatycznie na komputerze](#automatycznie-na-komputerze) | laptop/PC używany codziennie | co 30 min, gdy jesteś zalogowany |
| [24/7 na Raspberry Pi / serwerze](raspberry-pi.md) | „ustaw i zapomnij”, komendy w Telegramie o każdej porze | co 15 min, dzień i noc |

Wszystkie sposoby używają tych samych plików, więc możesz zacząć ręcznie i przejść na inny później. **Nigdy nie uruchamiaj tej samej konfiguracji na dwóch maszynach naraz**: zobacz [Przenosiny](#przenosiny-na-inną-maszynę).

## Ręcznie

| System | Jak |
|---|---|
| Windows | dwuklik **`sync.bat`** |
| macOS / Linux | `./sync.sh` w folderze projektu |
| dowolny | `python -m moodle_sync run` |

Gdy nie ma nic nowego, przebieg trwa kilka sekund. Pierwszy pobiera wszystko, więc może chwilę potrwać.

## Automatycznie na komputerze

Synchronizacja działa w tle co 30 minut, gdy jesteś zalogowany, a do tego zaraz po zalogowaniu. Przebieg przegapiony podczas uśpienia komputera ruszy po wybudzeniu. Wyjście trafia do `logs/sync.log`.

### Windows (Harmonogram zadań)

Kliknij dwukrotnie **`deploy\windows\schedule.bat`** albo w PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File deploy\windows\schedule.ps1              # co 30 min
powershell -ExecutionPolicy Bypass -File deploy\windows\schedule.ps1 -Minutes 60  # co godzinę
powershell -ExecutionPolicy Bypass -File deploy\windows\schedule.ps1 -Remove      # wyłącz
```

- Działa **w ukryciu** (`pythonw.exe`), więc nie wyskakuje okno co pół godziny.
- Nie są potrzebne uprawnienia administratora ani hasło, bo zadanie działa jako Ty, gdy jesteś zalogowany.
- Znajdziesz je w *Harmonogramie zadań → moodle-sync*.

### macOS

```bash
bash deploy/macos/schedule.sh           # co 30 min
bash deploy/macos/schedule.sh 60        # co godzinę
bash deploy/macos/schedule.sh --remove  # wyłącz
```

> **Ochrona prywatności:** macOS blokuje zadaniom w tle dostęp do folderów *Dokumenty*, *Biurko*, *Pobrane* i iCloud Drive, chyba że dasz „Pełny dostęp do dysku”.
> - Trzymaj projekt w katalogu domowym, np. `~/moodle-sync`.
> - Jeśli `DOWNLOAD_DIR` wskazuje do jednego z tych folderów, przenieś go albo daj pełny dostęp programowi `.venv/bin/python` (*Ustawienia systemowe → Prywatność i ochrona → Pełny dostęp do dysku*).

### Linux (komputer)

```bash
bash deploy/linux/schedule-user.sh           # co 30 min, timer systemd użytkownika
bash deploy/linux/schedule-user.sh --remove
```

Logi: `journalctl --user -u moodle-sync`. Żeby działało także po wylogowaniu, uruchom `sudo loginctl enable-linger $USER`.

## Jak często?

- **15–30 min** w zupełności wystarczy. Prowadzący nie wrzucają materiałów aż tak często, a każdy przebieg to kilkadziesiąt zapytań do serwera uczelni.
- **Nie schodź poniżej 15 minut.** Ogłoszenia i tak są sprawdzane najwyżej co 30 min, a oceny co godzinę.

## Przenosiny na inną maszynę

1. Wyłącz starą maszynę: usuń harmonogram (`-Remove` / `--remove`) i zatrzymaj bota.
2. Skopiuj na nową te pliki:
   - `.env`, `state.json`, `courses.json` / `przedmioty.json`,
   - `google_token.json` (jeśli używasz kalendarza),
   - `~/.config/rclone/rclone.conf` albo `%APPDATA%\rclone\rclone.conf` (jeśli używasz rclone).
3. Nie musisz kopiować `downloads/`. `state.json` wie, co już pobrano (i wysłano).

Dwie maszyny z tą samą konfiguracją pobierałyby te same pliki i wysyłały te same powiadomienia. Dwa boty Telegram z tym samym tokenem kłócą się o wiadomości (`409 Conflict`).

## Dlaczego nie „w chmurze” (GitHub Actions, darmowy hosting...)?

Brzmi kusząco: zero sprzętu. Świadomie tego nie polecamy:
- **Odpowiednik hasła uczelnianego w cudzej chmurze.** Token Moodle leżałby w zewnętrznym serwisie, a wyciek logu albo źle ustawiony publiczny fork by go ujawnił.
- **Stan między przebiegami:** zaplanowane zadania CI nie mają pamięci, więc zapamiętywanie, co pobrano, wymaga obejść (cache, commity), w których łatwo o błąd.
- **Niezawodność:** zaplanowane workflowy GitHuba bywają opóźniane w godzinach szczytu i są automatycznie wyłączane po 60 dniach bez aktywności w publicznych repozytoriach. Część uczelni blokuje też adresy IP centrów danych.

Laptop z Harmonogramem zadań albo Raspberry Pi za ~150 zł nie mają żadnego z tych problemów.
