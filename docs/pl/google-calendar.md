# Terminy w kalendarzu

🇬🇧 [English version](../en/google-calendar.md) · [← README](../../README.pl.md)

Są dwa sposoby:

| | **Kalendarz Google (synchronizacja)** | **Adres subskrypcji (dowolny kalendarz)** |
|---|---|---|
| Konfiguracja | ~10 min, jednorazowo | 1 min |
| Działa z | Kalendarzem Google | Google, Outlook, Apple, Thunderbird... |
| Aktualizacje | przy każdym przebiegu (15–30 min) | gdy aplikacja kalendarza odświeży (Google: do ~24 h) |
| ✅ dla oddanych zadań, własne przypomnienia, osobny kalendarz zajęć | ✅ | – |
| Powiadomienie o przesuniętym terminie | ✅ | – |

## Sposób 1: adres subskrypcji (bez konfiguracji)

```
python -m moodle_sync ics
```

Polecenie wypisze prywatny adres Twojego kalendarza Moodle. Dodaj go w aplikacji kalendarza:
- **Google:** *Inne kalendarze → + → Z adresu URL*
- **Outlook:** *Dodaj kalendarz → Subskrybuj z internetu*
- **Apple:** *Plik → Nowa subskrypcja kalendarza*

Adres zawiera tajny klucz, więc nie udostępniaj go.

## Sposób 2: synchronizacja z Kalendarzem Google

### Co dostajesz

Dwa nowe kalendarze:

| Kalendarz | Co w nim jest |
|---|---|
| **„<SITE_LABEL> – terminy”** | Terminy oddania zadań, otwarcie i zamknięcie quizów, wydarzenia dodane przez prowadzących. Przypomnienia dzień i 2 godziny wcześniej. |
| **„<SITE_LABEL> – zajęcia”** | Wpisy frekwencji, czyli w praktyce plan zajęć, bez przypomnień. Ukryjesz go jednym kliknięciem przy jego nazwie albo wyłączysz ustawieniem `SYNC_CLASSES=0`. |

- **Oddane** zadanie albo **ukończony** quiz dostaje **✅** i traci przypomnienia.
- Termin **przesunięty** przez prowadzącego jest aktualizowany, a Ty dostajesz powiadomienie.
- Wydarzenie usunięte w Moodle znika też z kalendarza.
- moodle-sync widzi **wyłącznie** kalendarze, które sam utworzył (zakres `calendar.app.created`), a nie Twój osobisty kalendarz.

> Terminy podane tylko tekstem (ogłoszenie, PDF) nie są wydarzeniami kalendarza. Te łapią [powiadomienia o ogłoszeniach](notifications.md).

### 1. Projekt w Google Cloud (raz, ~10 min)

Wejdź na <https://console.cloud.google.com> i zaloguj się kontem Google, którego kalendarza chcesz używać.

1. **Projekt:** kliknij listę projektów u góry → **New project** → nazwa `moodle-sync` → **Create**. Upewnij się, że jest wybrany.
2. **API:** ☰ → **APIs & Services → Library** → wyszukaj **Google Calendar API** → **Enable**. Jeśli będziesz używać rclone z Dyskiem Google, włącz też **Google Drive API**.
3. **Ekran zgody:** ☰ → **APIs & Services → OAuth consent screen**, w nowej konsoli *Google Auth Platform*. Kliknij **Get started**:
   - nazwa aplikacji `moodle-sync` i Twój e-mail,
   - **Audience: External**,
   - e-mail kontaktowy, akceptacja, **Create**.
4. **⚠️ Opublikuj aplikację:** w zakładce **Audience** kliknij **Publish app**, żeby status zmienił się na **In production**.

> W statusie *Testing* Google unieważnia logowanie po **7 dniach**, a synchronizacja po tygodniu po cichu przestałaby działać. Weryfikacja przez Google **nie** jest potrzebna. Przy logowaniu zobaczysz „Google nie zweryfikował tej aplikacji”: kliknij **Zaawansowane → Przejdź do moodle-sync**. To Twoja własna aplikacja.

5. **Klient:** **Google Auth Platform → Clients → Create client** → typ **Desktop app** → **Create** → **Download JSON**. Zapisz plik w folderze projektu jako **`client_secret.json`**.

### 2. Logowanie

```
python -m moodle_sync calendar --auth
```

Otworzy się przeglądarka. Po zalogowaniu powstanie `google_token.json`. Jest odpowiednikiem hasła, więc go nie udostępniaj. `client_secret.json` jest potrzebny tylko do tego kroku.

### 3. Test

```
python -m moodle_sync calendar --dry-run     # co zostałoby dodane
python -m moodle_sync calendar               # wykonaj
```

Od tej chwili kalendarz synchronizuje się przy każdym `python -m moodle_sync run`.

### Dostosowanie

Na górze pliku `moodle_sync/calendar_sync.py`:
- `REMINDERS` / `DEFAULT_REMINDERS`: minuty przed wydarzeniem,
- `PAST_DAYS` / `FUTURE_DAYS`: okno synchronizacji.

Nazwy kalendarzy pochodzą z `SITE_LABEL` i `LANGUAGE`. Zmieniaj je przed pierwszą synchronizacją; później zmienisz nazwę bezpośrednio w Kalendarzu Google.

Na Raspberry Pi wystarczy skopiować `google_token.json`. Przeglądarka nie jest tam potrzebna.
