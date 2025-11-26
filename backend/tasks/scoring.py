from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple, Any


DEFAULT_WEIGHTS = {
    "urgency": 0.4,
    "importance": 0.3,
    "effort": 0.1,
    "dependencies": 0.2,
}


def normalize(value: float, mn: float, mx: float) -> float:
    if mx == mn:
        return 0.5
    return (value - mn) / (mx - mn)


def detect_cycles(task_graph: Dict[str, Dict[str, Any]]) -> List[List[str]]:
    """
    Simple DFS-based cycle detector for dependency graph.
    task_graph: {id: {"dependencies": [ids...]}}
    """
    visited: Dict[str, str] = {}  # id -> "visiting" | "visited"
    stack: List[str] = []
    cycles: List[List[str]] = []

    def dfs(node: str):
        state = visited.get(node)
        if state == "visiting":
            # already in stack – cycle
            if node in stack:
                idx = stack.index(node)
                cycles.append(stack[idx:] + [node])
            return
        if state == "visited":
            return

        visited[node] = "visiting"
        stack.append(node)
        deps = task_graph.get(node, {}).get("dependencies", []) or []
        for dep in deps:
            if dep in task_graph:
                dfs(dep)
        stack.pop()
        visited[node] = "visited"

    for node in task_graph.keys():
        if node not in visited:
            dfs(node)

    return cycles


def compute_scores(
    tasks: List[Dict[str, Any]], weights: Dict[str, float] | None = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Core scoring logic.

    tasks: list of dicts with keys:
      - id (optional)
      - title
      - due_date (date or ISO string or None)
      - estimated_hours
      - importance
      - dependencies (list of ids)

    Returns:
      (sorted_scored_tasks, analysis_dict)
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    # Normalize weights to sum=1 to avoid weird configs
    total_w = sum(weights.values()) or 1.0
    weights = {k: v / total_w for k, v in weights.items()}

    # Build internal map with IDs
    task_map: Dict[str, Dict[str, Any]] = {}
    for idx, t in enumerate(tasks):
        tid = str(t.get("id") or f"T{idx}")
        deps = [str(d) for d in (t.get("dependencies") or [])]
        task_map[tid] = {
            "id": tid,
            "title": t.get("title", "").strip() or f"Task {idx+1}",
            "due_date": t.get("due_date"),
            "estimated_hours": float(t.get("estimated_hours") or 1.0),
            "importance": int(t.get("importance") or 5),
            "dependencies": deps,
            "raw": t,
        }

    # detect cycles
    cycles = detect_cycles(task_map)

    today = date.today()

    urgency_raw: List[float] = []
    importance_raw: List[float] = []
    effort_raw: List[float] = []
    deps_raw: List[int] = []

    # how many tasks each task is blocking
    blocked_count: Dict[str, int] = {tid: 0 for tid in task_map.keys()}
    for tid, info in task_map.items():
        for dep in info["dependencies"]:
            if dep in blocked_count:
                blocked_count[dep] += 1

    # build numeric vectors
    for tid, info in task_map.items():
        dd = info["due_date"]
        days_delta: float | None = None
        if dd:
            if isinstance(dd, str):
                try:
                    parsed = date.fromisoformat(dd)
                except ValueError:
                    parsed = None
            else:
                parsed = dd
            if parsed:
                days_delta = (parsed - today).days

        if days_delta is None:
            # no due date => neutral urgency
            urgency = 0.0
        else:
            # negative days (past) => higher urgency
            urgency = -float(days_delta)  # more negative -> more urgent -> bigger value here

        urgency_raw.append(urgency)
        importance_raw.append(info["importance"])
        effort_raw.append(max(0.1, info["estimated_hours"]))
        deps_raw.append(blocked_count.get(tid, 0))

    u_min, u_max = min(urgency_raw), max(urgency_raw)
    i_min, i_max = min(importance_raw), max(importance_raw)
    e_min, e_max = min(effort_raw), max(effort_raw)
    d_min, d_max = min(deps_raw), max(deps_raw)

    scored: List[Dict[str, Any]] = []

    for idx, (tid, info) in enumerate(task_map.items()):
        u_n = normalize(urgency_raw[idx], u_min, u_max)
        i_n = normalize(importance_raw[idx], i_min, i_max)
        e_n = 1.0 - normalize(effort_raw[idx], e_min, e_max)  # less effort => higher score
        d_n = normalize(deps_raw[idx], d_min, d_max)

        score_0_1 = (
            weights["urgency"] * u_n +
            weights["importance"] * i_n +
            weights["effort"] * e_n +
            weights["dependencies"] * d_n
        )
        score = round(score_0_1 * 100, 2)

        explanation_bits = [
            f"Urgency: {round(u_n * 100)}%",
            f"Importance: {round(i_n * 100)}%",
            f"Effort advantage: {round(e_n * 100)}%",
            f"Blocks {deps_raw[idx]} other task(s)",
        ]
        if cycles:
            explanation_bits.append("Warning: dependency cycle(s) detected in task list.")

        explanation = " | ".join(explanation_bits)

        scored.append({
            "id": tid,
            "title": info["title"],
            "due_date": info["due_date"],
            "estimated_hours": info["estimated_hours"],
            "importance": info["importance"],
            "dependencies": info["dependencies"],
            "score": score,
            "explanation": explanation,
        })

    scored_sorted = sorted(scored, key=lambda x: x["score"], reverse=True)

    analysis = {
        "weights": weights,
        "cycles": cycles,
        "summary": {
            "total_tasks": len(scored_sorted),
            "highest_score": scored_sorted[0]["score"] if scored_sorted else None,
        }
    }

    return scored_sorted, analysis


def suggest_top(
    tasks: List[Dict[str, Any]],
    top_n: int = 3,
    weights: Dict[str, float] | None = None,
) -> List[Dict[str, Any]]:
    scored, _ = compute_scores(tasks, weights=weights)
    return scored[:top_n]
