#!/usr/bin/env bash
# Registers a throw-away user, signs in and checks that the pages render and reach the Python server.
# Usage: scripts/smoke_test.sh [base_url]   (run `docker-compose up -d --build` first)
set -euo pipefail

BASE=${1:-http://localhost:3000}
JAR=$(mktemp)
trap 'rm -f "$JAR"' EXIT
EMAIL="smoke$(date +%s)@example.com"
PASSWORD='Smoke-Passw0rd!42'

csrf() { curl -fsS -b "$JAR" -c "$JAR" "$BASE/$1" | grep -o 'name="csrf" value="[^"]*"' | head -1 | sed 's/.*value="//;s/"//'; }
status() { curl -s -o /dev/null -w '%{http_code}' -b "$JAR" -c "$JAR" "$BASE/$1"; }
check() { [ "$2" = "$3" ] && echo "ok   $1" || { echo "FAIL $1: expected $3, got $2"; exit 1; }; }

check "login page" "$(status login.php)" 200
check "register page" "$(status register.php)" 200

curl -fsS -b "$JAR" -c "$JAR" -o /dev/null --data-urlencode "csrf=$(csrf register.php)" \
  --data-urlencode "name=Smoke Test" --data-urlencode "email=$EMAIL" \
  --data-urlencode "password=$PASSWORD" --data-urlencode "cpassword=$PASSWORD" "$BASE/register.php"
curl -fsS -b "$JAR" -c "$JAR" -o /dev/null --data-urlencode "csrf=$(csrf login.php)" \
  --data-urlencode "email=$EMAIL" --data-urlencode "password=$PASSWORD" "$BASE/login.php"

for page in index.php scraper.php profile.php discover.php mongo.php analytics.php crossval.php terms.php store.php usernames.php; do
  check "$page" "$(status "$page")" 200
done

# A rejected username proves the form, CSRF and validation work without needing the internet
reply=$(curl -fsS -b "$JAR" -c "$JAR" --data-urlencode "csrf=$(csrf profile.php)" \
  --data-urlencode "username=not a name" --data-urlencode "max_tweets=5" "$BASE/profile.php")
echo "$reply" | grep -q "Enter a valid X username" && echo "ok   profile validation" || { echo "FAIL profile validation"; exit 1; }

# Discover Profiles: selecting nothing is rejected by the page itself
reply=$(curl -fsS -b "$JAR" -c "$JAR" --data-urlencode "csrf=$(csrf discover.php)" \
  --data-urlencode "action=scrape" --data-urlencode "max_tweets=3" "$BASE/discover.php")
echo "$reply" | grep -q "Tick at least one profile" && echo "ok   discover validation" || { echo "FAIL discover validation"; exit 1; }

# A valid request is forwarded to the Python server, which answers (even if only with an error message)
reply=$(curl -fsS -b "$JAR" -c "$JAR" --data-urlencode "csrf=$(csrf profile.php)" \
  --data-urlencode "username=NA" --data-urlencode "max_tweets=1" "$BASE/profile.php")
if echo "$reply" | grep -qi "Cannot reach the Python server"; then
  echo "FAIL PHP cannot reach the Python server"; exit 1
fi
echo "ok   PHP reaches the Python server"

echo "All smoke checks passed"
