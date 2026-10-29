# Twitter / X API credentials

Only needed for the older API based collectors (timelines, followers, streaming). The X Scraper, X Profile Scraper,
Discover Profiles and all MongoDB pages work **without** any credentials.

**Never share or commit these values.** Set them as environment variables (preferred) or in
[config.ini](../data_collection_framework/config/config.ini):

- `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_KEY`, `TWITTER_ACCESS_SECRET`
- `TWITTER_BEARER_TOKEN` (streaming only)

## How to get them

1. Sign in at the [X Developer Portal](https://developer.x.com/en/portal/dashboard) and sign up for API access (the tier
   must allow what you use: timelines/followers need read access, streaming needs filtered stream).
2. Create a Project and an App inside it.
3. In the App's **Settings → User authentication settings**, enable OAuth 1.0a with **Read** permission (use *Read and
   write* only if you need it) and save. Set any callback/website URL, e.g. `http://localhost:3000`.
4. Open the App's **Keys and tokens** tab:
    - **API Key and Secret** → `TWITTER_CONSUMER_KEY` and `TWITTER_CONSUMER_SECRET`
    - **Access Token and Secret** → `TWITTER_ACCESS_KEY` and `TWITTER_ACCESS_SECRET`
      (generate them after step 3 so they carry the right permissions)
    - **Bearer Token** → `TWITTER_BEARER_TOKEN`
5. Copy each value right away (they are shown once; regenerate if lost) and export them, for example
   `export TWITTER_CONSUMER_KEY=...`, in the shell that starts `server.py`.

## API notes

- Tweets, followers and streaming use the Twitter API v2 (`tweepy.Client` / `tweepy.StreamingClient`,
  `tweepy>=4.14`); the old v1.1 endpoints are blocked for most accounts.
- Which calls work depends on your X API access tier (the Free tier allows almost no reads; timelines and followers
  need a paid tier). If a command fails with `403`, check the tier in the Developer Portal.
- Collected tweets are stored in a v1.1-like shape so the plots keep working.
- Streaming uses the v2 filtered stream and needs a bearer token. It replaces the app's existing stream rules with one
  rule matching any keyword; your access tier must allow filtered streams.
