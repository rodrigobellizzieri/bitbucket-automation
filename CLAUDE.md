# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

A Bitbucket Pipeline automation tool that creates new Bitbucket repositories with a single pipeline run. It: creates the repo via API, clones it, applies a template, pushes the template, creates `dev` and `prd` branches, sets the branching model, and enables pipelines — all driven by a Docker container (`rodrigobellizzieri/bitbucket-automation`).

## Running Locally

```bash
cd Code
pip install -r requirements.txt

# All env vars must be set before running
export BITBUCKET_WORKSPACE=...
export PROJECT=...
export REPOSITORY=...
export TEMPLATE=...
export PRIVATE=private   # "private" or "public"
export MAIN_BRANCHE=...
export DEV_BRANCHE=...
export CI_EMAIL=...
export CI_NAME=...
export BITBUCKET_USER=...
export BITBUCKET_PASS=...
export OAUTH_CLIENT_ID=...
export OAUTH_CLIENT_SECRET=...

python3 main.py
```

There is no test suite; run `python3 main.py` against a real Bitbucket workspace to validate changes.

## Building and Publishing the Docker Image

The GitHub Actions workflow (`.github/workflows/main.yml`) triggers on any push to a `v*` branch and publishes to Docker Hub as `rodrigobellizzieri/bitbucket-automation:latest` and `rodrigobellizzieri/bitbucket-automation:<tag>`.

To build locally:
```bash
docker build -t bitbucket-automation ./Code
```

Required GitHub secrets: `DOCKER_USER`, `DOCKER_PASS`.

**Releasing a new version:** After pushing a `v*` tag, manually update the image tag in `Documentation/example/bitbucket-pipelines.yml` (the `pipe: docker://rodrigobellizzieri/bitbucket-automation:<tag>` line) so users get the new version when they copy that file.

## Architecture

**`Code/main.py`** — the entire application logic in a single script. Execution is linear (no CLI args, no config files):
1. Reads all config from environment variables, validates none are `None`, normalizes casing.
2. Gets an OAuth2 bearer token via `client_credentials` grant.
3. Calls functions sequentially: `createRepository` → `cloneRepository` → `setTemplate` → `pushTemplate` → `createBranches(main)` → `createBranches(dev)` → `updateBrancheModel` → `enablePipeline`.

All Bitbucket API calls use `https://api.bitbucket.org/2.0/repositories/{workspace}/{repository}` as the base URL with Bearer token auth. The `BITBUCKET_PASS` (app password) is used only for `git clone` via HTTPS, not for the REST API.

**`Documentation/example/bitbucket-pipelines.yml`** — the pipeline file that users copy into their central repository. It defines the `bitbucket-automation` custom pipeline and maps UI variables to the Docker pipe. Note: the UI variable is named `PRD_BRANCHE` but is passed to the container as `MAIN_BRANCHE` — these two names refer to the same branch and must be kept in sync if the pipeline YAML is modified.

**`Documentation/example/templates/`** — example template directories. The `TEMPLATE` variable must exactly match a subdirectory name under `templates/` in the central repo at runtime. At runtime inside Docker (workdir `/`), `setTemplate()` resolves templates from `/templates/`, which is the pipeline workspace root — so the central repo must have a `templates/` directory at its root.

**`Models/variables-model.json`** — a reference model showing example variable structures for environment-specific (dev/hmg/prd) and repository-level Bitbucket deployment variables. Not read by `main.py`; used as documentation/reference.

## Key Constraints

- `PRIVATE` accepts only `"private"` or `"public"` (lowercased at runtime); any other value causes `createRepository` to silently skip the API call with no exit, leaving subsequent steps to fail.
- Branches are created from `master` (hardcoded `"hash": "master"` in `createBranches`); the target repo must have a `master` branch at creation time.
- Creating a branch named `master` is explicitly blocked.
- The `pushTemplate` function contains commented-out git branch creation code — branch creation now goes through the Bitbucket API (`createBranches`) instead.
- When updating `allowed-values` in `bitbucket-pipelines.yml`, the `templates/` directory in the central repo must have matching subdirectory names.
- The OAuth Consumer must have **Admin** access to both Projects and Repositories in Bitbucket; lower permissions cause silent API failures.
