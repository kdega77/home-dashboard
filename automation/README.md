# Making the dashboard refresh independent of Muse

## Headlines — move to GitHub Actions (runs on GitHub, ~2 min setup)

1. Open the repo on github.com: **kdega77/home-dashboard**
2. Click **Add file → Create new file**.
3. In the filename box type exactly: `.github/workflows/headlines.yml`
4. Open `automation/github-actions-headlines.yml` in this repo, copy its
   full contents, and paste them into the new file.
5. Click **Commit changes**.
6. (Optional check) Open the **Actions** tab — the "headlines" workflow
   should appear; you can run it once with **Run workflow** to test.

From then on GitHub itself refreshes `headlines.json` every 30 minutes.
Tell Muse once it's in and Muse will retire the headlines half of its
own refresh job so nothing double-runs.

## Steps — why it can't live on GitHub

Step counts live in Apple Health on the iPhone; GitHub has no way to read
them. Something with Health access has to bridge them. Options:

- Muse's 30-minute job (current setup — fully automatic, nothing to do).
- An iPhone **Shortcuts automation**: reads today's Health steps and
  uploads `steps.json` to this repo with a fine-grained GitHub token.
  Ask Muse for the step-by-step if you want this route.
