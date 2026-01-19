#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# SNDS simple fetcher (interactive) using .env config
# - Always writes into ./data/
# - Output filenames always include the *requested* date tag

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

if [[ ! -r "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

: "${SNDS_KEY:?SNDS_KEY is not set in .env}"
: "${BASE_URL:?BASE_URL is not set in .env}"
: "${DATA_PATH:?DATA_PATH is not set in .env}"
: "${IPSTATUS_PATH:?IPSTATUS_PATH is not set in .env}"
: "${OUT_SUBDIR:?OUT_SUBDIR is not set in .env}"

OUT_DIR="${SCRIPT_DIR}/${OUT_SUBDIR}"
mkdir -p "$OUT_DIR"

to_mmddyy_pst() {
  local iso="$1"
  TZ="America/Los_Angeles" date -d "$iso" +%m%d%y
}

validate_iso_date() {
  local iso="$1"
  date -d "$iso" >/dev/null 2>&1
}

read -r -p "Which date would like to see? (YYYY-MM-DD) of Enter voor 'latest available': " INPUT_DATE

DATE_PARAM=""
REQUEST_TAG=""

if [[ -n "$INPUT_DATE" ]]; then
  if ! validate_iso_date "$INPUT_DATE"; then
    echo "Invalid date: '$INPUT_DATE' (use ex. 2025-11-01)" >&2
    exit 1
  fi

  MMDDYY="$(to_mmddyy_pst "$INPUT_DATE")"
  DATE_PARAM="&date=${MMDDYY}"
  REQUEST_TAG="$INPUT_DATE"
else
  # Latest available has no explicit date in the response URL; we still want a history filename tag.
  # So we ask what date you want to store it as.
  read -r -p "Enter chosen. Choose date to save? (YYYY-MM-DD): " STORE_DATE
  if ! validate_iso_date "$STORE_DATE"; then
    echo "Invalid date: '$STORE_DATE'" >&2
    exit 1
  fi
  REQUEST_TAG="$STORE_DATE"
fi

DATA_URL="${BASE_URL}${DATA_PATH}?key=${SNDS_KEY}${DATE_PARAM}"
IP_URL="${BASE_URL}${IPSTATUS_PATH}?key=${SNDS_KEY}"

DATA_OUT="${OUT_DIR}/snds-data-${REQUEST_TAG}.csv"
IP_OUT="${OUT_DIR}/snds-ipStatus-${REQUEST_TAG}.csv"

echo
echo "Downloading:"
echo "  DATA     : $DATA_URL"
echo "  IPSTATUS : $IP_URL"
echo
echo "Saving to:"
echo "  $DATA_OUT"
echo "  $IP_OUT"
echo

curl -sS -L --fail -o "$DATA_OUT" "$DATA_URL" || {
  echo "Download failed (DATA). Perhaps an error 204 - No Content or something else." >&2
  exit 1
}

curl -sS -L --fail -o "$IP_OUT" "$IP_URL" || {
  echo "Download failed (ipStatus)." >&2
  exit 1
}

echo "Done."
echo "  $(wc -c < "$DATA_OUT") bytes  -> $DATA_OUT"
echo "  $(wc -c < "$IP_OUT") bytes  -> $IP_OUT"

