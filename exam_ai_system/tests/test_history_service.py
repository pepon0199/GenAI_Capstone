from history.service import ExamHistoryService


class FakeQuery:
    def __init__(self, store):
        self.store = store
        self.user_id = None
        self.limit_value = None

    def insert(self, payload):
        self.store.append(
            {
                "id": len(self.store) + 1,
                "created_at": "2026-04-04T00:00:00Z",
                **payload,
            }
        )
        return self

    def select(self, fields):
        return self

    def eq(self, column, value):
        self.user_id = value
        return self

    def order(self, column, desc=False):
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def execute(self):
        filtered = [
            row for row in reversed(self.store) if self.user_id is None or row["user_id"] == self.user_id
        ]
        if self.limit_value is not None:
            filtered = filtered[: self.limit_value]
        return type("Response", (), {"data": filtered})()


class FailingQuery:
    def insert(self, payload):
        return self

    def select(self, fields):
        return self

    def eq(self, column, value):
        return self

    def order(self, column, desc=False):
        return self

    def limit(self, value):
        return self

    def execute(self):
        raise RuntimeError("supabase unavailable")


class FakeClient:
    def __init__(self):
        self.store = []

    def table(self, table_name):
        assert table_name == "exam_attempts"
        return FakeQuery(self.store)


def test_record_and_list_attempts():
    client = FakeClient()
    history_service = ExamHistoryService(lambda: client)

    history_service.record_attempt(
        user_id="user-1",
        topic="Python",
        exam_type="Practice Exam",
        level="Beginner",
        question_count=5,
        score=4,
        percentage=80.0,
        provider="groq",
    )

    attempts = history_service.list_attempts("user-1")

    assert len(attempts) == 1
    assert attempts[0]["topic"] == "Python"
    assert attempts[0]["score"] == 4


def test_record_attempt_wraps_storage_failures():
    class FailingClient:
        def table(self, table_name):
            return FailingQuery()

    history_service = ExamHistoryService(lambda: FailingClient())

    try:
        history_service.record_attempt(
            user_id="user-1",
            topic="Python",
            exam_type="Practice Exam",
            level="Beginner",
            question_count=5,
            score=4,
            percentage=80.0,
            provider="groq",
        )
    except RuntimeError as exc:
        assert "Unable to save exam history" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError for history save failure")


def test_list_attempts_wraps_storage_failures():
    class FailingClient:
        def table(self, table_name):
            return FailingQuery()

    history_service = ExamHistoryService(lambda: FailingClient())

    try:
        history_service.list_attempts("user-1")
    except RuntimeError as exc:
        assert "Unable to load exam history" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError for history load failure")
