# Data Collection Framework

Collects tweets, followers and streams, stores them in MongoDB and analyses them.
A PHP web UI (login + command forms) talks to a Python command server.

```
Browser ──► PHP (Apache, :3000) ──JSON over TCP──► Python server.py (:5555) ──► MongoDB / Twitter API
                │
              MariaDB (users)
```

### Prerequisites

- `Python 3.8+` and `Docker` installed
- Twitter API credentials (DON'T SHARE OR COMMIT THEM). Set them as environment variables (preferred) or in
  [config.ini](data_collection_framework/config/config.ini):
    * `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_KEY`, `TWITTER_ACCESS_SECRET` (and
      `TWITTER_BEARER_TOKEN` for streaming)
    * How to get them:
        1. Sign in at the [X Developer Portal](https://developer.x.com/en/portal/dashboard) and sign up for API access
           (the tier must allow what you use: timelines/followers need read access, streaming needs filtered stream).
        2. Create a Project and an App inside it.
        3. In the App's **Settings → User authentication settings**, enable OAuth 1.0a with **Read** permission (use
           *Read and write* only if you need it) and save. Set any callback/website URL, e.g. `http://localhost:3000`.
        4. Open the App's **Keys and tokens** tab:
            * **API Key and Secret** → `TWITTER_CONSUMER_KEY` and `TWITTER_CONSUMER_SECRET`
            * **Access Token and Secret** → `TWITTER_ACCESS_KEY` and `TWITTER_ACCESS_SECRET`
              (generate them after step 3 so they carry the right permissions)
            * **Bearer Token** → `TWITTER_BEARER_TOKEN`
        5. Copy each value right away (they are shown once; regenerate if lost) and export them:
           `export TWITTER_CONSUMER_KEY=...` (and so on) in the shell that starts `server.py`.
- Optional: copy [.env.example](.env.example) to `.env` and change the passwords/token (defaults work for local dev)

---

### How to Run the Application

1. `docker-compose up -d --build` (MariaDB, phpMyAdmin, PHP app, MongoDB, mongo-express)
2. Start the Python server (the first run creates `.venv` and installs all packages automatically):
    1. `make server` (reads `PY_SERVER_TOKEN` and `TWITTER_*` from the environment or from `.env`)
       works from any directory: `make -f /path/to/data-collection-framework/Makefile server`
    2. Without `make`, from the project root (`.venv` is created in the current directory):
       `python3 -m venv .venv && .venv/bin/python -m pip install -r data_collection_framework/requirements.txt`,
       then `.venv/bin/python data_collection_framework/server.py` (the script itself runs from any directory)
3. Open http://localhost:3000/, sign up, sign in and run commands.

The **X Scraper** page (`/scraper.php`) collects public X pages for keywords you enter (web search + Jina Reader, no X
API credits) into MongoDB `x_batch_db.tweets_by_keywords`. The same job runs from a terminal with
`python data_collection_framework/x_batch_scraper.py "keyword" --live 60`.

The **X Profile Scraper** page (`/profile.php`) follows the approach of
the [Proxidize Twitter scraper article](https://proxidize.com/blog/twitter-scraper/): a Playwright browser opens a
profile and captures the GraphQL JSON that X's web app loads while scrolling (tweet text, engagement, views, media,
hashtags, profile details) instead of parsing HTML. It adds a reusable login session, checkpoints with resume, JSON/CSV
export (`data_collection_framework/x_profile_data/<user>/`), MongoDB storage (`x_profile_db.profile_tweets`), an
engagement summary and an optional proxy (`X_PROXY=host:port[:user:password]`). Without a login (the default) it reads
the public profile page, which gives the latest handful of posts. For deeper scrolling, click **Connect X account** on
the page (or run `make browsers` then `make x-login`): a sign-in window opens on the machine running `server.py` and,
once you are signed in by any method, the session is saved automatically and used from then on. Terminal
use: `.venv/bin/python data_collection_framework/x_profile_scraper.py user NASA --max 100 --resume`. Not taken over from
the article: automation-flag hiding and randomized "human" timing, and the OpenAI analysis (the summary is local). Use
your own account and respect X's terms; X may still limit or block automated access.

The **MongoDB Data** page (`/mongo.php`) lists your MongoDB databases with their collections and document counts; click
a collection to see its newest 20 documents.

Prefer a console instead of the web UI? Run `make menu` (it uses the same commands).

Networking notes:

- The PHP container reaches the server through `host.docker.internal`.
- Docker Desktop (macOS/Windows) works with the default `127.0.0.1` bind. On Linux set
  `PY_SERVER_HOST=0.0.0.0` for the server and **always set `PY_SERVER_TOKEN`**, because the server executes commands.

---

### How to Test the Application

```
make test
```

Manual check: http://localhost:3000/ → Sign up → Sign in.

GitHub Actions (`.github/workflows/ci.yml`) runs on every push and pull request: pytest on Python 3.12, a
`php -l` syntax check of `src/`, and a smoke test (`scripts/smoke_test.sh`) that starts the Python server and the PHP
app with MariaDB, signs up and in, loads the pages and checks that PHP reaches the Python server. Run the smoke test
locally against a running stack with `bash scripts/smoke_test.sh`.

---

### Services in [docker-compose.yml](docker-compose.yml)

| Service           | URL                       | Credentials                                                |
|-------------------|---------------------------|------------------------------------------------------------|
| PHP app           | http://localhost:3000     | sign up in the UI                                          |
| phpMyAdmin        | http://localhost:8080     | MariaDB user/password from `.env` (default `user`)         |
| mongo-express     | http://localhost:8081     | `mexpress` / `MONGO_EXPRESS_PASSWORD` (default `mexpress`) |
| MariaDB / MongoDB | bound to `127.0.0.1` only | see `.env.example`                                         |

---

### Project layout

- `src/` PHP front end (PDO + prepared statements, `password_hash`, CSRF tokens, escaped output)
    - `lib/` small classes: `Database`, `UserRepository`, `Auth`, `Csrf`, `PythonServerClient`, `CommandCatalog`
    - `index.php` renders every command form from `CommandCatalog` (no per-command code)
- `data_collection_framework/` Python back end
    - `commands/` Command pattern: `base.py` (Command, Param validators, registry) and `definitions.py`
    - `server.py` thin socket loop; `menu.py` console UI; both only call the registry
    - `config/settings.py` lazy, immutable settings (env vars override the config file)
    - `storage/` shared MongoDB client/repository (batched inserts) and streaming file readers
    - collectors (`TweetCollector`, `FollowerCollector`, `StreamCollector`, `MongoWriter`) receive their dependencies
      by injection
    - `Analysis` is table-driven (one `Metric` per plot), `nlp/` holds n-grams, tokenization and term statistics

### Adding a command

1. Python: register a `Command(name, title, params, handler)` in `commands/definitions.py`.
2. PHP: add the same name and fields to `src/lib/CommandCatalog.php`.

The Python side is authoritative for validation; the PHP side only checks required/numeric values.

### Other settings in [config.ini](data_collection_framework/config/config.ini)

- `word_list_for_streaming` comma separated keywords for `streamfromlist`
- `file_path_for_*` / `streaming_txt_file` data folders (relative to `data_collection_framework/`, created on start):
    - `file_path_for_list_of_username`: `*.txt` files with Twitter usernames (whitespace separated)
    - `file_path_for_mongo`: `*.txt` files with one tweet JSON per line (used by store data and the plots)
    - `streaming_txt_file`: where streamed tweets are written (used by term frequency)
    - `file_path_for_cross_val`: at least 2 sub folders (one per class) with text files
- `mongo_uri` (or `MONGO_URI`), `PY_SERVER_HOST`, `PY_SERVER_PORT`, `PY_SERVER_TOKEN`

### Notes

- Old MD5 password hashes are not migrated; the schema (`db_scripts/`) only runs on a fresh DB volume
  (`docker-compose down -v` to reset).
- Tweets, followers and streaming use the Twitter API v2 (`tweepy.Client` / `tweepy.StreamingClient`, `tweepy>=4.14`);
  the old v1.1 endpoints are blocked for most accounts. Which calls work depends on your X API access tier (the Free
  tier allows almost no reads; timelines and followers need a paid tier). If a command fails with `403`, check the tier
  in the Developer Portal. Collected tweets are stored in a v1.1-like shape so the plots keep working.
- Streaming uses the Twitter API v2 filtered stream (`tweepy.StreamingClient`, `tweepy>=4.14`) and needs a bearer token.
  It replaces the app's existing stream rules with one rule matching any keyword; your API access tier must allow
  filtered streams.
