# Upload instructions

## GitHub

Authenticate first:

```bash
gh auth login -h github.com
```

Then, from this release directory:

```bash
git remote add origin git@github.com:<USER_OR_ORG>/hydrological-state-monitoring-limits.git
git branch -M main
git push -u origin main
gh release create v1.0.0-round9 \
  hydrological-state-monitoring-limits-public-release.zip \
  --title "v1.0.0-round9 public data and code release" \
  --notes "Public-safe derived source data and lightweight code for the hydrological state-monitoring limits article."
```

## Zenodo

Use the GitHub-Zenodo integration after the GitHub repository is public, or
upload `hydrological-state-monitoring-limits-public-release.zip` manually through
the Zenodo web interface. The `.zenodo.json` file in this directory contains the
prepared metadata. Do not place access credentials in this repository.
