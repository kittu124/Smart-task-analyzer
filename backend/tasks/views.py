import json
from typing import Dict

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import TaskInputSerializer
from .scoring import compute_scores, suggest_top


def _extract_weights(query_params) -> Dict[str, float] | None:
    """
    Optional query: ?urgency=0.5&importance=0.3&effort=0.1&dependencies=0.1
    """
    keys = ["urgency", "importance", "effort", "dependencies"]
    if not any(k in query_params for k in keys):
        return None
    try:
        weights = {k: float(query_params.get(k)) for k in keys if query_params.get(k) is not None}
        return weights
    except (TypeError, ValueError):
        return None


@api_view(["POST"])
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/

    Body: [ {task1}, {task2}, ... ]

    Returns:
      {
        "tasks": [ scored tasks ... ],
        "analysis": { ... }
      }
    """
    data = request.data
    if not isinstance(data, list):
        return Response(
            {"error": "Expected a JSON array of tasks."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    validated = []
    for idx, item in enumerate(data):
        serializer = TaskInputSerializer(data=item)
        if not serializer.is_valid():
            return Response(
                {"error": f"Invalid task at index {idx}", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        validated.append(serializer.validated_data)

    weights = _extract_weights(request.query_params)
    scored, analysis = compute_scores(validated, weights=weights)
    return Response({"tasks": scored, "analysis": analysis})


@api_view(["GET"])
def suggest(request):
    """
    GET /api/tasks/suggest/?tasks=<json-encoded-array>

    Example:
      /api/tasks/suggest/?tasks=[{"title":"A","importance":8,...},...]

    Returns top 3 suggested tasks with explanations.
    """
    tasks_param = request.query_params.get("tasks")
    if not tasks_param:
        return Response(
            {"error": "Provide tasks as JSON in `tasks` query parameter."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        raw_tasks = json.loads(tasks_param)
    except json.JSONDecodeError:
        return Response(
            {"error": "Invalid JSON in `tasks` query parameter."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(raw_tasks, list):
        return Response(
            {"error": "`tasks` must be a JSON array."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    validated = []
    for idx, item in enumerate(raw_tasks):
        serializer = TaskInputSerializer(data=item)
        if not serializer.is_valid():
            return Response(
                {"error": f"Invalid task at index {idx}", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        validated.append(serializer.validated_data)

    weights = _extract_weights(request.query_params)
    top_tasks = suggest_top(validated, top_n=3, weights=weights)
    return Response({"suggestions": top_tasks})
