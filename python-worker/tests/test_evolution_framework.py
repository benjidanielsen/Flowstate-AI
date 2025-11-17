import unittest
import sys
import os
import types
import importlib.machinery
from datetime import datetime
from unittest import mock

# Add parent directory to path
package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, package_root)

dummy_package = types.ModuleType("evolution_framework")
dummy_package.__path__ = [os.path.join(package_root, "evolution_framework")]
dummy_package.__spec__ = importlib.machinery.ModuleSpec(
    "evolution_framework", loader=None, is_package=True
)
sys.modules.setdefault("evolution_framework", dummy_package)


class _DummyCursor:
    def execute(self, *args, **kwargs):
        return None

    def close(self):
        return None


class _DummyConnection:
    def __init__(self):
        self.closed = False

    def cursor(self):
        return _DummyCursor()

    def commit(self):
        return None


def _dummy_connect(*args, **kwargs):
    return _DummyConnection()


dummy_psycopg2 = types.ModuleType("psycopg2")
dummy_psycopg2.connect = _dummy_connect

dummy_psycopg2_extras = types.ModuleType("psycopg2.extras")
dummy_psycopg2_extras.Json = lambda value: value

dummy_psycopg2.extras = dummy_psycopg2_extras
sys.modules.setdefault("psycopg2", dummy_psycopg2)
sys.modules.setdefault("psycopg2.extras", dummy_psycopg2_extras)


class _DummySentenceTransformer:
    def __init__(self, *args, **kwargs):
        self._dim = 384

    def encode(self, content):
        return [0.0] if isinstance(content, str) else [[0.0] for _ in content]

    def get_sentence_embedding_dimension(self):
        return self._dim


dummy_sentence_transformers = types.ModuleType("sentence_transformers")
dummy_sentence_transformers.SentenceTransformer = _DummySentenceTransformer
sys.modules.setdefault("sentence_transformers", dummy_sentence_transformers)


class _DummyQdrantClient:
    def __init__(self, *args, **kwargs):
        self.collection_name = None

    def get_collections(self):
        return types.SimpleNamespace(collections=[types.SimpleNamespace(name="flowstate_knowledge")])

    def create_collection(self, *args, **kwargs):
        self.collection_name = kwargs.get("collection_name")

    def upsert(self, *args, **kwargs):
        return None

    def search(self, *args, **kwargs):
        return []


class _DummyDistance:
    COSINE = "cosine"


class _DummyVectorParams:
    def __init__(self, size, distance):
        self.size = size
        self.distance = distance


class _DummyPointStruct:
    def __init__(self, id, vector, payload):
        self.id = id
        self.vector = vector
        self.payload = payload


class _DummyFilter:
    def __init__(self, must=None):
        self.must = must or []


class _DummyFieldCondition:
    def __init__(self, key, match=None):
        self.key = key
        self.match = match


class _DummyMatchValue:
    def __init__(self, value):
        self.value = value


dummy_qdrant_client = types.ModuleType("qdrant_client")
dummy_qdrant_client.QdrantClient = _DummyQdrantClient

dummy_qdrant_models = types.ModuleType("qdrant_client.models")
dummy_qdrant_models.Distance = _DummyDistance
dummy_qdrant_models.VectorParams = _DummyVectorParams
dummy_qdrant_models.PointStruct = _DummyPointStruct
dummy_qdrant_models.Filter = _DummyFilter
dummy_qdrant_models.FieldCondition = _DummyFieldCondition
dummy_qdrant_models.MatchValue = _DummyMatchValue

dummy_qdrant_client.models = dummy_qdrant_models
sys.modules.setdefault("qdrant_client", dummy_qdrant_client)
sys.modules.setdefault("qdrant_client.models", dummy_qdrant_models)

from evolution_framework.metrics_collector import MetricsCollector
from evolution_framework.knowledge_manager import VectorKnowledgeManager
from evolution_framework.code_analyzer import CodeAnalyzer
from evolution_framework.anomaly_detector import AnomalyDetector
from evolution_framework.evolution_governor import EvolutionGovernor
from evolution_framework.config import EvolutionConfig
from evolution_framework.xai_nba import XAINBA
from evolution_framework.human_oversight_manager import HumanOversightManager


class DummyKnowledgeManager:
    def __init__(self):
        self.records = []

    def store_knowledge(self, key, value, tags=None):
        self.records.append((key, value, tags or []))

    def add_knowledge(self, content, category, source, confidence=1.0, metadata=None):
        self.records.append(
            {
                "content": content,
                "category": category,
                "source": source,
                "confidence": confidence,
                "metadata": metadata or {},
            }
        )


class DummyMetricsCollector:
    def get_current_timestamp(self):
        return "2024-01-01T00:00:00Z"


class DummyEvolutionManager:
    def __init__(self):
        self.metrics_collector = DummyMetricsCollector()
        self.events = {}

    def create_evolution_event(
        self,
        event_type,
        component,
        description,
        proposed_by,
        status="proposed",
        metrics_before=None,
        metrics_after=None,
        metadata=None,
    ):
        event_id = f"evt_{len(self.events) + 1}"
        self.events[event_id] = {
            "id": event_id,
            "type": event_type,
            "component": component,
            "description": description,
            "proposed_by": proposed_by,
            "status": status,
            "metrics_before": metrics_before or {},
            "metrics_after": metrics_after or {},
            "metadata": metadata or {},
            "timestamp": self.metrics_collector.get_current_timestamp(),
        }
        return event_id

    def update_evolution_event(self, event_id, status=None, metrics_after=None, metadata=None):
        event = self.events.get(event_id)
        if not event:
            return False
        if status:
            event["status"] = status
        if metrics_after:
            event["metrics_after"] = metrics_after
        if metadata:
            event["metadata"].update(metadata)
        return True

    def get_evolution_events(self, event_type=None, component=None, status=None, limit=50):
        events = list(self.events.values())
        if event_type:
            events = [event for event in events if event["type"] == event_type]
        if component:
            events = [event for event in events if event["component"] == component]
        if status:
            events = [event for event in events if event["status"] == status]
        return events[:limit]


class DummyGovernor:
    pass

class TestEvolutionFramework(unittest.TestCase):
    
    def test_metrics_collector(self):
        """Ensure MetricsCollector can record and fetch metrics with a stub connection."""

        class StubCursor:
            def __init__(self, db_state):
                self.db_state = db_state
                self._results = []
                self.rowcount = 0

            def execute(self, query, params=None):
                sql = " ".join(query.split()).lower()
                params = params or []
                if "insert into performance_metrics" in sql:
                    record = {
                        "id": len(self.db_state["records"]) + 1,
                        "timestamp": datetime.now(),
                        "metric_name": params[0],
                        "value": params[1],
                        "unit": params[2],
                        "component": params[3],
                        "context": params[4],
                    }
                    self.db_state["records"].append(record)
                    self.rowcount = 1
                elif sql.startswith("select"):
                    component = params[0]
                    idx = 1
                    metric_name = None
                    since = None
                    if "metric_name = %s" in query:
                        metric_name = params[idx]
                        idx += 1
                    if "timestamp >= %s" in query:
                        since = params[idx]
                        idx += 1
                    limit = params[idx] if idx < len(params) else len(self.db_state["records"])
                    filtered = [
                        record for record in self.db_state["records"]
                        if record["component"] == component
                    ]
                    if metric_name:
                        filtered = [r for r in filtered if r["metric_name"] == metric_name]
                    if since:
                        filtered = [r for r in filtered if r["timestamp"] >= since]
                    self._results = [
                        (
                            r["id"],
                            r["timestamp"],
                            r["metric_name"],
                            r["value"],
                            r["unit"],
                            r["component"],
                            r["context"],
                        )
                        for r in filtered[:limit]
                    ]
                elif sql.startswith("delete from performance_metrics"):
                    component = params[0]
                    cutoff = params[1]
                    before = len(self.db_state["records"])
                    self.db_state["records"] = [
                        r for r in self.db_state["records"]
                        if not (r["component"] == component and r["timestamp"] < cutoff)
                    ]
                    self.rowcount = before - len(self.db_state["records"])

            def fetchall(self):
                return self._results

            def close(self):
                return None

        class StubConnection:
            def __init__(self, db_state):
                self.db_state = db_state
                self.closed = False

            def cursor(self):
                return StubCursor(self.db_state)

            def commit(self):
                return None

            def close(self):
                self.closed = True

        db_state = {"records": []}
        stub_connection = StubConnection(db_state)

        collector = MetricsCollector(
            "test_component", config=EvolutionConfig(database_url="postgresql://localhost/testdb")
        )
        collector._conn = stub_connection
        collector._get_connection = lambda: stub_connection

        self.assertTrue(collector.record_metric("test_metric", 100, "ms", {"source": "unit"}))
        metrics = collector.get_metrics("test_metric")
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["value"], 100)
    
    def test_code_analyzer(self):
        """Test code analysis"""
        analyzer = CodeAnalyzer()
        test_code = """
def simple_function():
    return 42
"""
        with mock.patch(
            "evolution_framework.code_analyzer.mi_visit",
            return_value=[75.0],
        ):
            result = analyzer.analyze_code(test_code)
        self.assertIsNotNone(result)
        self.assertIn("complexity", result)
        self.assertIn("maintainability", result)
    
    def test_anomaly_detector(self):
        """Test anomaly detection"""
        class StubMetricsCollectorForAnomaly:
            def __init__(self):
                self.values = [100] * 10

            def get_metric_stats(self, metric_name, component=None, limit=None):
                return {"count": len(self.values)}

            def get_metric_values(self, metric_name, component=None, limit=None):
                return self.values + [1000]

        detector = AnomalyDetector(StubMetricsCollectorForAnomaly(), window_size=5)
        is_anomaly, details = detector.detect_anomaly("test_metric")
        self.assertTrue(is_anomaly)
    
    def test_evolution_governor(self):
        """Test evolution governance"""
        class StubMetricsCollectorForGovernor:
            def __init__(self):
                self.records = []

            def record_metric(self, name, value, unit="", context=""):
                self.records.append((name, value, unit, context))

        class StubAnomalyDetector:
            def __init__(self):
                self.detected = []

            def get_anomaly_report(self, hours=1):
                return {"total_anomalies": 0}

        collector = StubMetricsCollectorForGovernor()
        detector = StubAnomalyDetector()
        governor = EvolutionGovernor(
            DummyEvolutionManager(),
            detector,
            collector,
            DummyKnowledgeManager(),
            EvolutionConfig(database_url="postgresql://localhost/testdb"),
        )

        # Test safe mode activation
        governor.activate_safe_mode("test_reason")
        self.assertTrue(governor.safe_mode_active)

        # Test safe mode deactivation
        governor.deactivate_safe_mode()
        self.assertFalse(governor.safe_mode_active)

    def test_xai_nba_handles_serialization_errors(self):
        knowledge_manager = DummyKnowledgeManager()
        xai_nba = XAINBA(knowledge_manager)

        recommendation = {
            "id": "rec-123",
            "action_type": "offer_discount",
            "confidence": 0.92,
            "non_serializable": {"ids"},
        }
        context = {
            "customer_segment": "vip",
            "customer_history": {"last_purchase_date": "2024-05-01"},
            "product_interest": ["sneakers", "apparel"],
        }

        explanation = xai_nba.explain_nba_recommendation(recommendation, context)

        self.assertEqual(explanation["recommendation"]["id"], "rec-123")
        self.assertTrue(knowledge_manager.records)
        stored_payload = knowledge_manager.records[0][1]
        self.assertIsInstance(stored_payload, str)

    def test_human_oversight_manager_instantiation_and_flow(self):
        dummy_manager = DummyEvolutionManager()
        dummy_governor = DummyGovernor()
        config = EvolutionConfig(database_url="postgresql://localhost/testdb")
        oversight_manager = HumanOversightManager(dummy_manager, dummy_governor, config)

        event_id = oversight_manager.request_human_approval(
            "Deploy new reminder workflow",
            {"component": "reminder_service"},
            urgency="high",
        )
        self.assertIsNotNone(event_id)
        self.assertIn(event_id, dummy_manager.events)

        approval_recorded = oversight_manager.record_human_decision(
            event_id,
            decision="approve",
            rationale="Test rationale",
            decision_maker="QA Analyst",
        )
        self.assertTrue(approval_recorded)
        self.assertEqual(oversight_manager.get_pending_approvals(), [])
        self.assertEqual(oversight_manager.check_human_decision(event_id), "approved")

if __name__ == '__main__':
    unittest.main()
