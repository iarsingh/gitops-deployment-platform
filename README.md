# GitOps Deployment Platform

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/gitops/main.py`](src/gitops/main.py) | HTTP handlers: `POST /compare` |
| [`src/gitops/compare.py`](src/gitops/compare.py) | Functions: `compare` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/gitops/__init__.py`](src/gitops/__init__.py) | Deployment manifests or chart templates |
| [`tests/test_gitops.py`](tests/test_gitops.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn gitops.main:app --reload
```

<!-- project-guide:end -->

Level: 14 — Cloud, DevOps, platform

Skills: Python, desired state, drift

Compare desired image and replicas with the observed record. Name the fields that differ. `applied` stays false. Git, not this API, is the writer.

```bash
pip install -r requirements.txt
pytest -q
```

## Ops plane

Workspaces, tenant isolation, job approval, and audit live under `/v1`. Production apply is refused. See `docs/ARCHITECTURE.md`.
