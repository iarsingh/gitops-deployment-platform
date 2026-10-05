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
    M2 -->|imports| M1
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/gitops/main.py`](src/gitops/main.py) | HTTP handlers: `POST /compare` |
| [`src/gitops/compare.py`](src/gitops/compare.py) | Functions: `compare` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/gitops/__init__.py`](src/gitops/__init__.py) | Deployment manifests or chart templates |
| [`tests/test_gitops.py`](tests/test_gitops.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `POST /compare` | `post_compare` | [`src/gitops/main.py`](src/gitops/main.py#L7) |

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

## Data flow and design decisions

### What is the input-to-output contract of `compare`

In [`src/gitops/compare.py`](src/gitops/compare.py#L1), `compare(desired, observed)` receives the inputs. The function computes these intermediate values:

- `diffs = [key for key in ('image', 'replicas') if desired[key] != observed[key]]`

Its result is defined by:

- `{'drifted': bool(diffs), 'diffs': diffs, 'applied': False}`

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_gitops.py`](tests/test_gitops.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.
