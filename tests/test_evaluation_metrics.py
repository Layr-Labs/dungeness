"""Challenge metrics must be data, not assumptions in the display layer."""
import unittest

from dungeness.evaluation_metrics import evaluation_metrics


class EvaluationMetricsTests(unittest.TestCase):
    def test_explicit_metrics_are_authoritative_and_numeric(self):
        data = {"legacy_value": 12, "metrics": {
            "zero": 0, "negative": -2, "fraction": 0.25,
            "boolean": True, "text": "42", "nested": {"value": 2},
            "missing": None, "infinity": float('inf'), "nan": float('nan'),
            "overflow": 10 ** 400, "": 1,
        }}
        self.assertEqual(evaluation_metrics(data), {"zero": 0, "negative": -2, "fraction": 0.25})
        for explicit in ({}, None, [], "malformed"):
            with self.subTest(explicit=explicit):
                self.assertEqual(evaluation_metrics({"legacy_value": 12, "metrics": explicit}), {})

    def test_legacy_metrics_exclude_standard_event_metadata(self):
        self.assertEqual(evaluation_metrics({
            "score": 2, "best_score": 1, "duration_ms": 10, "sequence": 3,
            "submissions_used": 1, "submissions_remaining": 3, "submissions_limit": 4,
            "throughput": 5.5, "memory_bytes": 1024,
        }), {"throughput": 5.5, "memory_bytes": 1024})
