# gitops-deployment-platform — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does gitops-deployment-platform address, and what can you demonstrate?

Compare desired image and replicas with the observed record. Name the fields that differ. `applied` stays false. Git, not this API, is the writer.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/gitops/main.py`](src/gitops/main.py): Deployment manifests or chart templates.
- [`src/gitops/compare.py`](src/gitops/compare.py): Deployment manifests or chart templates.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/gitops/__init__.py`](src/gitops/__init__.py): Deployment manifests or chart templates.
- [`tests/test_gitops.py`](tests/test_gitops.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `compare` and explain the decision it makes?

The main walkthrough here is `compare(desired, observed)` in [`src/gitops/compare.py`](src/gitops/compare.py#L1).

```python
def compare(desired, observed):
    diffs = [key for key in ("image", "replicas") if desired[key] != observed[key]]
    return {"drifted": bool(diffs), "diffs": diffs, "applied": False}
```

The implementation calls `bool`. In an interview, trace those calls in execution order using a fixture input.

## 4. Where would you add input-validation tests?

Start with the handlers `post_compare` in [`src/gitops/main.py`](src/gitops/main.py#L7). Use the request schema or body access in each handler to build valid, missing-field, wrong-type, and boundary inputs. I would inspect existing tests before claiming coverage.

## 5. Which test would you use to demonstrate correctness?

[`tests/test_gitops.py`](tests/test_gitops.py#L4) contains `test_drift_is_reported_and_not_applied`:

```python
def test_drift_is_reported_and_not_applied():
    client = TestClient(app)
    drifted = client.post("/compare", json={"desired": {"image": "billing:1.4.2", "replicas": 2}, "observed": {"image": "billing:1.4.2", "replicas": 5}}).json()
    assert drifted["drifted"] is True
    assert drifted["diffs"] == ["replicas"]
    assert drifted["applied"] is False
    matched = client.post("/compare", json={"desired": {"image": "billing:1.4.2", "replicas": 2}, "observed": {"image": "billing:1.4.2", "replicas": 2}}).json()
    assert matched["drifted"] is False
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 6. What HTTP interface does the code expose?

- `POST /compare` → `post_compare` in [`src/gitops/main.py`](src/gitops/main.py#L7).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 7. How would you investigate data ownership and persistence?

Trace the data/configuration files and the code that reads or writes them in the component table. Identify which files are examples, which records are mutable, and which external store is actually configured. I would document those facts before discussing retention, backup, or tenant isolation.

## 8. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 9. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 10. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 11. What is the input-to-output contract of `compare`?

In [`src/gitops/compare.py`](src/gitops/compare.py#L1), `compare(desired, observed)` receives the inputs. The function computes these intermediate values:

- `diffs = [key for key in ('image', 'replicas') if desired[key] != observed[key]]`

Its result is defined by:

- `{'drifted': bool(diffs), 'diffs': diffs, 'applied': False}`
