# Going Concern — Sleeper dashboard

Automatically publishes an updated read-only fantasy football dashboard from Sleeper's public API.

## Setup on GitHub
1. Create a **public** repository (suggested: `sleeper-going-concern`).
2. Upload `update.py`, `site/index.html`, and `.github/workflows/update.yml` **preserving folder paths**. If GitHub's web upload flattens the folders, create/edit the files by their exact paths instead.
3. Go to **Settings → Pages** and choose **GitHub Actions** as the Build and deployment source.
4. Go to **Actions → Update Sleeper dashboard → Run workflow**.
5. After the deployment finishes, open `https://YOUR-GITHUB-USERNAME.github.io/sleeper-going-concern/`.

The workflow runs at 12:00 and 22:00 UTC daily (7 AM / 5 PM EST; 8 AM / 6 PM EDT). GitHub's scheduled workflows may run late or be paused due to repository inactivity. The dashboard visibly displays the last successful update time.

## Data and limitations
- Sleeper league ID: `1397672130383990784`; username: `kenneysc`.
- Includes starters, bench, reserve, record, waiver position, league-wide unrostered players, and current-week team transactions.
- Searchable unrostered list does not distinguish free agents from players on waivers and is **not** an expert ranking.
- Pages and its `data.json` are **public** on a public repository. They contain league roster information available via Sleeper's public endpoints.
- Sleeper's API is read-only. This project cannot submit lineup changes or waiver claims.
- This dashboard is a scheduled snapshot, not a continuous connection to ChatGPT. ChatGPT reviews require fetching the published data URL; they cannot be assumed to do so automatically.
