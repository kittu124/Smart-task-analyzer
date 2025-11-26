from datetime import date, timedelta

from django.test import TestCase

from .scoring import compute_scores, detect_cycles, suggest_top


class ScoringTests(TestCase):
    def test_past_due_has_higher_priority(self):
        today = date.today()
        tasks = [
            {
                "id": "past",
                "title": "Past due",
                "due_date": str(today - timedelta(days=3)),
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": [],
            },
            {
                "id": "future",
                "title": "Future",
                "due_date": str(today + timedelta(days=5)),
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": [],
            },
        ]
        scored, _ = compute_scores(tasks)
        self.assertEqual(scored[0]["id"], "past")

    def test_importance_affects_score(self):
        tasks = [
            {
                "id": "low",
                "title": "Low importance",
                "due_date": None,
                "estimated_hours": 1,
                "importance": 2,
                "dependencies": [],
            },
            {
                "id": "high",
                "title": "High importance",
                "due_date": None,
                "estimated_hours": 1,
                "importance": 9,
                "dependencies": [],
            },
        ]
        scored, _ = compute_scores(tasks)
        self.assertEqual(scored[0]["id"], "high")

    def test_dependencies_increase_priority(self):
        tasks = [
            {
                "id": "root",
                "title": "Unblocker",
                "due_date": None,
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": [],
            },
            {
                "id": "child",
                "title": "Depends on root",
                "due_date": None,
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": ["root"],
            },
        ]
        scored, _ = compute_scores(tasks)
        # root blocks another task, so should rank higher or close
        self.assertEqual(scored[0]["id"], "root")

    def test_suggest_top_returns_three_or_less(self):
        tasks = [
            {"id": f"t{i}", "title": f"T{i}", "due_date": None, "estimated_hours": 1, "importance": i, "dependencies": []}
            for i in range(1, 6)
        ]
        suggestions = suggest_top(tasks, top_n=3)
        self.assertLessEqual(len(suggestions), 3)
