# Web UI pages

All pages need a sign in (sign up on first use). The left menu links to each of them.

## Collecting

**X Scraper** (`/scraper.php`) collects public X pages for keywords you enter (web search + Jina Reader, no X API
credits) into MongoDB `x_batch_db.tweets_by_keywords`. The same job runs from a terminal with
`python data_collection_framework/x_batch_scraper.py "keyword" --live 60`.

**X Profile Scraper** (`/profile.php`) follows the approach of the
[Proxidize Twitter scraper article](https://proxidize.com/blog/twitter-scraper/): a Playwright browser opens a profile
and captures the GraphQL JSON that X's web app loads while scrolling (tweet text, engagement, views, media, hashtags,
profile details) instead of parsing HTML.

- Adds a reusable login session, checkpoints with resume, JSON/CSV export
  (`data_collection_framework/x_profile_data/<user>/`), MongoDB storage (`x_profile_db.profile_tweets`), an engagement
  summary and an optional proxy (`X_PROXY=host:port[:user:password]`).
- Without a login (the default) it reads the public profile page, which gives the latest handful of posts.
- For deeper scrolling click **Connect X account** on the page (or run `make browsers` then `make x-login` on your
  machine; the Docker container cannot open a window): a sign-in
  window opens locally and, once you are signed in by any method, the session is saved
  automatically and used from then on.
- Terminal use: `.venv/bin/python data_collection_framework/x_profile_scraper.py user NASA --max 100 --resume`.
- Not taken over from the article: automation-flag hiding, randomized "human" timing and the OpenAI analysis (the
  summary is local). Use your own account and respect X's terms; X may still limit or block automated access.

**Discover Profiles** (`/discover.php`) builds a list of X usernames without any X login: pick a letter and web search
(the same engines as the X Scraper) is asked for profiles starting with it, or add usernames by hand.

- They are stored in MongoDB `x_profile_db.discovered_profiles` and listed alphabetically with checkboxes; tick up to 5
  and press **Scrape selected** to collect their newest posts one after another.
- An optional topic (for example `Java developer`) keeps only results whose title or snippet mention it, and lets you
  filter the list by that topic later.
- Search returns only a few names per try, so the list is neither random nor complete.

**Collecting Tweets & Followers** (Main Page menu) are the older API and file based collectors and streaming
commands. The "from the user list" forms read usernames from a file; use **Load usernames file**
(`/usernames.php`) to replace it from your computer (an example template can be downloaded there).

## Storing and browsing

**Store Data in MongoDB** (`/store.php`) lists every `.txt` file (one JSON document per line) found in the configured
data folders, and lets you upload files from your computer. Tick the files, choose a database and collection (or
create new ones) and load them; the list refreshes itself whenever a collector adds files.

**MongoDB Data** (`/mongo.php`) lists your databases with their collections and document counts; click a collection to
see its documents. Collections whose documents have a `username` (such as `profile_tweets`) are grouped by profile:
each profile is a dropdown with its tweet count, and opening one loads only that profile's tweets, 10 per page (served
by an index on `username`). Other collections show a flat list, newest first.

## Analysing

**Analytics & Charts** (`/analytics.php`) computes statistics from any stored collection: tweets, likes, retweets,
views or replies per profile, most liked tweets, hashtags, frequent terms, terms that appear together, word and
character n-grams, tweet/media types and tweets by date. Show them as a table with bars, a column chart or a pie
chart, for all profiles or a single one.

**Cross Validation (MongoDB)** (`/crossval.php`) trains a TF-IDF + linear SVM classifier that guesses which profile
wrote a tweet (or any label field you choose) and reports k-fold accuracy, F1 macro, shuffle-split scores and a
confusion matrix with charts. It needs at least two labels with as many documents as folds.

**Term Frequency (MongoDB)** (`/terms.php`) counts the most common terms, hashtags and co-occurring word pairs of any
text field.

## Settings

**Settings** (`/settings.php`, visible only to the first registered account) edits `config.ini` and `.env` from the
browser: database connection, Twitter API keys, streaming keywords, data folders, server port/token and database
passwords.

- Secrets (keys, tokens, passwords, the Mongo URI) are never shown again. Leave one empty to keep it, type a new value
  to replace it, or tick *clear* to remove it.
- Values are validated (folders must be relative, no quotes or `$` in secrets); comments in the files are kept.
- If `.env` does not exist yet, it is created with just the values you change; other settings keep their defaults.
- In Docker only `config.ini` is editable here (`.env` is read by Compose); `MONGO_URI` comes from Compose.
- Changes apply after restarting the Python server (`docker compose restart python-api`) (and `docker compose up -d` for
  values that Docker reads). Database passwords in `.env` do not change an existing MariaDB/MongoDB volume.

## Console

Prefer a console instead of the web UI? Run `make menu` (it uses the same commands).
