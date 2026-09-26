import json
import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "agent_execution.log")

logger = logging.getLogger("multi_agent")
if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class MessageBus:
    def emit(self, message):
        record = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "task_id": message.task_id,
            "from_agent": message.from_agent,
            "to_agent": message.to_agent,
            "message_type": message.message_type,
            "status": message.status,
        }
        logger.info(json.dumps(record, ensure_ascii=False))

    def log_retry(self, task_id: str, attempt: int, errors: list[str]):
        record = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "task_id": task_id,
            "event": "retry",
            "attempt": attempt,
            "errors": errors,
        }
        logger.info(json.dumps(record, ensure_ascii=False))
