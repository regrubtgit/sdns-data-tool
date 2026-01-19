# Microsoft SNDS CLI Tools

**Version:** 0.1.0  
**Note:** This project was created with help from ChatGPT ("vibe coding").

Small, user-level command line tools to download and inspect Microsoft SNDS
(Sender Network Data Services) CSV exports.

This repository is intentionally simple:
- no background daemons
- no system-wide automation
- no external Python dependencies

Everything runs as a normal user from the shell.

---

## What is SNDS?

Microsoft SNDS (Sender Network Data Services) provides daily insight into
mail traffic, complaint rates, and IP reputation for sending IP addresses.

Microsoft offers an **Automated Data Access** feature that allows CSV downloads
via HTTPS using a read-only access key. This project uses that mechanism.

---

## Directory Structure

```
snds/
├── .env                # Configuration (URLs, access key) - NOT committed
├── .env.example        # Example configuration (safe to commit)
├── snds-fetch.sh       # Bash script to download SNDS CSV files
├── snds-show.py        # Python CLI to view CSV data in the terminal
├── data/               # Historical CSV files (by requested date) - NOT committed
└── README.md
```

---

## Configuration (`.env`)

All configurable values are stored in `.env` so the scripts never need to be
modified when URLs or endpoints change.

Example:

```
SNDS_KEY="your-snds-access-key"
BASE_URL="https://sendersupport.olc.protection.outlook.com/snds"

DATA_PATH="/data/"
IPSTATUS_PATH="/ipStatus/"
OUT_SUBDIR="data"
```

**Security note:**  
The SNDS key is read-only but should still be treated as sensitive.

```
chmod 600 .env
```

Recommendation: commit an `.env.example` and keep `.env` ignored.

---

## Downloading Data (`snds-fetch.sh`)

`snds-fetch.sh` downloads CSV files from SNDS and stores them in `data/`
using filenames that include the requested date.

### Run interactively

```
./snds-fetch.sh
```

You will be asked:
- which date to request (`YYYY-MM-DD`)
- or press Enter to fetch the latest available data

Files are saved as:

```
data/
├── snds-data-YYYY-MM-DD.csv
└── snds-ipStatus-YYYY-MM-DD.csv
```

### Important SNDS behavior

- SNDS may return **empty CSV files**
- This is normal and usually means:
  - no traffic for that IP/date
  - or no data available yet
- HTTP 204 (No Content) is a valid response

Empty files are still useful for historical tracking.

---

## Viewing Data on the CLI (`snds-show.py`)

`snds-show.py` parses the CSV files and prints a readable table in the terminal.

No third-party libraries are required.

### Show data for a specific date

```
./snds-show.py --date 2025-11-01
```

### Show only one dataset

```
./snds-show.py --type data --date 2025-11-01
./snds-show.py --type ipstatus --date 2025-11-01
```

### Limit output rows

```
./snds-show.py --date 2025-11-01 --limit 20
```

### Select columns (DATA only)

```
./snds-show.py --type data --date 2025-11-01 --columns "IP,Date,Traffic,ComplaintRate"
```

If column names differ or are unknown, the script falls back to showing the
first few available columns.

---

## Python Requirements

- Python 3.9+
- Standard library only (`csv`, `argparse`, `gzip`, `pathlib`)

---

## Design Philosophy

- Simple Bash for downloading
- Python only for parsing and presentation
- No cron, no systemd, no background services
- Explicit user intent for every action
- Easy to audit and modify

---

## Limitations

- SNDS CSV schemas may change over time
- Column names are not guaranteed
- Some days will legitimately have empty CSV files

This project intentionally does **not** attempt to normalize or validate SNDS
data beyond basic CSV parsing.

---

## License

MIT License — see `LICENSE`.

---

# Microsoft SNDS CLI Tools (Nederlands)

**Versie:** 0.1.0  
**Opmerking:** Dit project is gemaakt met hulp van ChatGPT ("vibe coding").

Kleine command-line tools om Microsoft SNDS (Sender Network Data Services)
CSV-exports te downloaden en te bekijken.

Alles draait als **gewone gebruiker**, zonder services of automatische taken.

---

## Wat is SNDS?

Microsoft SNDS geeft inzicht in mailverkeer, klachtpercentages en reputatie
van verzendende IP-adressen.

Via **Automated Data Access** stelt Microsoft CSV-bestanden beschikbaar die
met een HTTPS-sleutel kunnen worden opgehaald. Deze scripts gebruiken die
functionaliteit.

---

## Structuur

```
snds/
├── .env
├── .env.example
├── snds-fetch.sh
├── snds-show.py
├── data/
└── README.md
```

---

## Configuratie

Alle URLs en de toegangssleutel staan in `.env`.
Scripts hoeven niet aangepast te worden bij wijzigingen.

Let op: de sleutel is read-only, maar wél gevoelig.

Advies: commit `.env.example` en zet `.env` in `.gitignore`.

---

## Data ophalen

```
./snds-fetch.sh
```

- Je kiest een datum (`YYYY-MM-DD`)
- Of je haalt de meest recente beschikbare data op

Bestanden worden historisch opgeslagen in `data/`.

Lege CSV-bestanden zijn **normaal gedrag** bij SNDS.

---

## Data bekijken in de terminal

```
./snds-show.py --date 2025-11-01
```

De Python tool leest de CSV en toont een tabel op de CLI.
Geen externe libraries nodig.

---

## Ontwerpkeuzes

- Zo min mogelijk magie
- Volledig transparant
- Alles handmatig en controleerbaar
- Geschikt voor audit, troubleshooting en analyse

---

## Beperkingen

- SNDS levert soms lege bestanden
- Kolomnamen kunnen wijzigen
- Geen validatie of normalisatie van Microsoft-data

Dit is bewust zo gehouden.

---

## Licentie

MIT License — zie `LICENSE`.

