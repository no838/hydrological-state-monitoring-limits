# Upload instructions

Current upload status: **not uploaded yet**.

The local package has passed the public-release sanitization check and has
been committed locally. External upload is blocked until GitHub and Zenodo
authentication are completed through secure login flows. Do not paste private
access strings into chat, repository files, manuscripts or shell history.

## GitHub

Authenticate first:

```bash
gh auth login -h github.com
```

Then, from this release directory:

```bash
gh repo create <USER_OR_ORG>/hydrological-state-monitoring-limits \
  --public \
  --source=. \
  --remote=origin \
  --push
gh release create v1.0.0-round9 \
  ../hydrological-state-monitoring-limits-public-release.zip \
  --title "v1.0.0-round9 public data and code release" \
  --notes "Public-safe derived source data and lightweight code for the hydrological state-monitoring limits article."
```

If the repository already exists, use:

```bash
git remote add origin git@github.com:<USER_OR_ORG>/hydrological-state-monitoring-limits.git
git branch -M main
git push -u origin main
gh release create v1.0.0-round9 \
  ../hydrological-state-monitoring-limits-public-release.zip \
  --title "v1.0.0-round9 public data and code release" \
  --notes "Public-safe derived source data and lightweight code for the hydrological state-monitoring limits article."
```

## Zenodo

Use the GitHub-Zenodo integration after the GitHub repository is public, or
upload `hydrological-state-monitoring-limits-public-release.zip` manually through
the Zenodo web interface. The `.zenodo.json` file in this directory contains the
prepared metadata. Do not place private access strings in this repository.
