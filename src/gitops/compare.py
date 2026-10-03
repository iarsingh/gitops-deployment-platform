def compare(desired, observed):
    diffs = [key for key in ("image", "replicas") if desired[key] != observed[key]]
    return {"drifted": bool(diffs), "diffs": diffs, "applied": False}
