# gitops-deployment-platform — project architecture

[README](README.md) · [Interview questions and answers](INTERVIEW_QA.md)

## Purpose and scope

Compare desired image and replicas with the observed record. Name the fields that differ. `applied` stays false. Git, not this API, is the writer.

This document describes files and symbols in this checkout. Deployment templates and statements in the original overview are distinguished from a verified running environment.

## Component diagram

```mermaid
flowchart LR
    M0["src/gitops/__init__.py"]
    M1["src/gitops/compare.py"]
    M2["src/gitops/main.py"]
    M3["src/gitops/ops.py"]
    M2 -->|imports| M1
    M2 -->|imports| M3
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/gitops/main.py`](src/gitops/main.py) | HTTP handlers: `POST /compare` |
| [`src/gitops/ops.py`](src/gitops/ops.py) | HTTP handlers: `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}` |
| [`src/gitops/compare.py`](src/gitops/compare.py) | Functions: `compare` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/gitops/__init__.py`](src/gitops/__init__.py) | Deployment manifests or chart templates |
| [`Dockerfile`](Dockerfile) | Container build/service configuration |
| [`Makefile`](Makefile) | Implementation or supporting configuration |
| [`docker-compose.yml`](docker-compose.yml) | Container build/service configuration |
| [`tests/test_gitops.py`](tests/test_gitops.py) | Executable checks and regression examples |
| [`tests/test_ops.py`](tests/test_ops.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Project explanations or operating notes |

## Existing design and operating guides

These checked-in guides provide the project’s detailed design, operational context, or deployment view:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `POST /compare` | `post_compare` | [`src/gitops/main.py`](src/gitops/main.py#L9) |
| `GET /readyz` | `readyz` | [`src/gitops/ops.py`](src/gitops/ops.py#L44) |
| `POST /workspaces` | `create_workspace` | [`src/gitops/ops.py`](src/gitops/ops.py#L49) |
| `GET /workspaces` | `list_workspaces` | [`src/gitops/ops.py`](src/gitops/ops.py#L66) |
| `POST /workspaces/{workspace_id}/jobs` | `create_job` | [`src/gitops/ops.py`](src/gitops/ops.py#L73) |
| `GET /jobs/{job_id}` | `get_job` | [`src/gitops/ops.py`](src/gitops/ops.py#L96) |
| `POST /jobs/{job_id}/approve` | `approve_job` | [`src/gitops/ops.py`](src/gitops/ops.py#L105) |
| `GET /audit` | `audit` | [`src/gitops/ops.py`](src/gitops/ops.py#L122) |
| `GET /metrics` | `metrics` | [`src/gitops/ops.py`](src/gitops/ops.py#L138) |

The table lists literal route decorators found in the inspected Python modules. Router prefixes and middleware can add behavior; check the linked handler and application setup before calling an endpoint.

## Implementation walkthrough

### `compare(desired, observed)`

Source: [`src/gitops/compare.py`](src/gitops/compare.py#L1).

Calls visible in this function: `bool`.

```python
def compare(desired, observed):
    diffs = [key for key in ("image", "replicas") if desired[key] != observed[key]]
    return {"drifted": bool(diffs), "diffs": diffs, "applied": False}
```

## Validation and failure paths

| Explicit exception | Source |
| --- | --- |
| `HTTPException(status_code=404, detail='workspace not found')` | [`src/gitops/ops.py`](src/gitops/ops.py#L77) |
| `HTTPException(status_code=404, detail='job not found')` | [`src/gitops/ops.py`](src/gitops/ops.py#L100) |
| `HTTPException(status_code=404, detail='job not found')` | [`src/gitops/ops.py`](src/gitops/ops.py#L109) |
| `HTTPException(status_code=403, detail='production apply is disabled in this lab')` | [`src/gitops/ops.py`](src/gitops/ops.py#L113) |

These are explicit exceptions in the inspected source, rather than a claim that every failure is handled. Follow the calling handler to see whether the exception becomes an HTTP response or propagates.

## Data and state

- [`src/gitops/ops.py`](src/gitops/ops.py) defines module-level containers: `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`.

Module-level dictionaries/lists live in a Python process. They can be fixtures or mutable state; inspect writes before treating them as persistent storage. A production extension would need to define persistence and concurrency behavior explicitly.

## Data flow and design decisions

### What is the input-to-output contract of `compare`

In [`src/gitops/compare.py`](src/gitops/compare.py#L1), `compare(desired, observed)` receives the inputs. The function computes these intermediate values:

- `diffs = [key for key in ('image', 'replicas') if desired[key] != observed[key]]`

Its result is defined by:

- `{'drifted': bool(diffs), 'diffs': diffs, 'applied': False}`

### What does the operations plane add, and where is its limit

[`src/gitops/ops.py`](src/gitops/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_gitops.py`](tests/test_gitops.py), [`tests/test_ops.py`](tests/test_ops.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.
