# Upload Blockers

Status as of 2026-06-10: **external upload not completed**.

## GitHub

`gh auth status` reports that the active GitHub account `no838` is not
authenticated. Re-authenticate through the GitHub CLI before upload:

```bash
gh auth login -h github.com
```

Do not paste GitHub private access strings into chat, repository files,
manuscripts or shell history.

## Zenodo

No Zenodo authentication material is present in the runtime environment. Upload
through the Zenodo web interface or authenticate through a secure local
environment.
The prepared metadata file is `.zenodo.json`.

Do not place Zenodo private access strings in this repository.

## Ready Local Artifacts

- release directory: `hydrological-state-monitoring-limits-public-release/`
- release archive: `../hydrological-state-monitoring-limits-public-release.zip`
- local git commit: `cf69eb8` plus any subsequent upload-instruction commits
- sanitization report: `PUBLIC_RELEASE_SANITIZATION_REPORT.md`
