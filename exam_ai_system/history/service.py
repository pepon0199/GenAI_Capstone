class ExamHistoryService:
    def __init__(self, client_factory):
        self.client_factory = client_factory

    def record_attempt(
        self,
        user_id,
        topic,
        exam_type,
        level,
        question_count,
        score,
        percentage,
        provider,
    ):
        client = self.client_factory()
        try:
            client.table("exam_attempts").insert(
                {
                    "user_id": user_id,
                    "topic": topic,
                    "exam_type": exam_type,
                    "level": level,
                    "question_count": question_count,
                    "score": score,
                    "percentage": percentage,
                    "provider": provider,
                }
            ).execute()
        except Exception as exc:
            raise RuntimeError("Unable to save exam history right now.") from exc

    def list_attempts(self, user_id, limit=10):
        client = self.client_factory()
        try:
            response = (
                client.table("exam_attempts")
                .select(
                    "id, topic, exam_type, level, question_count, score, percentage, "
                    "provider, created_at"
                )
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
        except Exception as exc:
            raise RuntimeError("Unable to load exam history right now.") from exc
        return list(getattr(response, "data", []) or [])
