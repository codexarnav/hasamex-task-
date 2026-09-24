"""Application-specific exceptions."""
from uuid import UUID


class InsightOSError(Exception):
    """Base exception for InsightOS."""

    def __init__(self, message: str, detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class NotFoundError(InsightOSError):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: UUID | str):
        super().__init__(
            message=f"{resource} not found",
            detail=f"{resource} with id '{resource_id}' does not exist",
        )
        self.resource = resource
        self.resource_id = resource_id


class ProjectNotFoundError(NotFoundError):
    def __init__(self, project_id: UUID | str):
        super().__init__("Project", project_id)


class GuideNotFoundError(NotFoundError):
    def __init__(self, project_id: UUID | str):
        super().__init__("InterviewGuide", project_id)


class TranscriptNotFoundError(NotFoundError):
    def __init__(self, transcript_id: UUID | str):
        super().__init__("Transcript", transcript_id)


class ExpertNotFoundError(NotFoundError):
    def __init__(self, expert_id: UUID | str):
        super().__init__("Expert", expert_id)


class EvidenceNotFoundError(NotFoundError):
    def __init__(self, evidence_id: UUID | str):
        super().__init__("Evidence", evidence_id)


class ParsingError(InsightOSError):
    """Error during file parsing."""
    pass


class LLMError(InsightOSError):
    """Error communicating with LLM."""
    pass


class LLMStructuredOutputError(LLMError):
    """LLM returned unparseable structured output."""
    pass


class EmbeddingError(InsightOSError):
    """Error generating embeddings."""
    pass


class VectorStoreError(InsightOSError):
    """Error communicating with vector store."""
    pass


class EvidenceValidationError(InsightOSError):
    """Evidence reference validation failed."""
    pass


class InsufficientEvidenceError(InsightOSError):
    """Not enough evidence to generate a grounded response."""
    pass


class FileStorageError(InsightOSError):
    """Error with file storage operations."""
    pass


class AnalysisError(InsightOSError):
    """Error during analysis pipeline."""
    pass


class ProjectIsolationError(InsightOSError):
    """Cross-project data access attempted."""

    def __init__(self, detail: str = "Cross-project data access is not permitted"):
        super().__init__(message="Project isolation violation", detail=detail)


class UploadError(InsightOSError):
    """Error during file upload."""
    pass
