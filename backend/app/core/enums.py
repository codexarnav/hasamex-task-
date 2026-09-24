"""Status enums used throughout the application."""
import enum


class ProjectStatus(str, enum.Enum):
    """Project lifecycle status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GuideStatus(str, enum.Enum):
    """Interview guide processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptStatus(str, enum.Enum):
    """Transcript processing status."""
    UPLOADED = "uploaded"
    PARSING = "parsing"
    EMBEDDING = "embedding"
    READY = "ready"
    FAILED = "failed"


class AnalysisStatus(str, enum.Enum):
    """Analysis pipeline status."""
    PENDING = "pending"
    RETRIEVING = "retrieving"
    CLASSIFYING = "classifying"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
