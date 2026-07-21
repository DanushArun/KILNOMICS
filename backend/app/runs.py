"""In-memory status for active local workbook analysis runs."""

from dataclasses import dataclass
from threading import Lock
from uuid import uuid4


@dataclass
class TrainingRun:
    """One active workbook analysis and its completed milestones."""

    phase: str = "queued"
    progress_pct: int = 0
    result: dict[str, object] | None = None
    error: str | None = None


class RunStore:
    """Thread-safe local storage for short-lived analysis progress."""

    def __init__(self) -> None:
        self._runs: dict[str, TrainingRun] = {}
        self._lock = Lock()

    def create(self) -> str:
        """Create and return a new queued analysis run."""
        run_id = str(uuid4())
        with self._lock:
            self._runs[run_id] = TrainingRun()
        return run_id

    def update(self, run_id: str, phase: str, progress_pct: int) -> None:
        """Record a completed milestone for a known run."""
        with self._lock:
            run = self._get(run_id)
            run.phase = phase
            run.progress_pct = progress_pct

    def complete(self, run_id: str, result: dict[str, object]) -> None:
        """Record the final response after every analysis stage has completed."""
        with self._lock:
            run = self._get(run_id)
            run.phase = "complete"
            run.progress_pct = 100
            run.result = result

    def fail(self, run_id: str, error: str) -> None:
        """Record a terminal error for the caller to display."""
        with self._lock:
            run = self._get(run_id)
            run.phase = "failed"
            run.error = error

    def snapshot(self, run_id: str) -> dict[str, object]:
        """Return the current run state without exposing mutable internals."""
        with self._lock:
            run = self._get(run_id)
            return {
                "phase": run.phase,
                "progress_pct": run.progress_pct,
                "result": run.result,
                "error": run.error,
            }

    def _get(self, run_id: str) -> TrainingRun:
        try:
            return self._runs[run_id]
        except KeyError as error:
            raise ValueError(f"Unknown analysis run: {run_id}") from error
