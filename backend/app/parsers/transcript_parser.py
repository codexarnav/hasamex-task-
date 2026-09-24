"""Transcript parser.

Parses interview transcript text into structured utterances.
Handles multiple common transcript formats:
  - Timestamp range format: "00:12:31 - 00:12:46"
  - Single timestamp format: "[00:12:31]"
  - Speaker-line format with or without timestamps

The parser is tolerant of formatting variations.
Timestamps come from the transcript - never invented.
"""
import re
from dataclasses import dataclass, field

from app.core.exceptions import ParsingError
from app.core.logging import get_logger

logger = get_logger("parsers.transcript")

# Patterns for timestamp detection
# Format: "HH:MM:SS - HH:MM:SS" or "MM:SS - MM:SS"
TIMESTAMP_RANGE_PATTERN = re.compile(
    r'(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—]\s*(\d{1,2}:\d{2}(?::\d{2})?)'
)

# Format: "[HH:MM:SS]", "(HH:MM:SS)", or bare "HH:MM:SS" / "MM:SS" on its own line
SINGLE_TIMESTAMP_PATTERN = re.compile(
    r'^[\[\(]?(\d{1,2}:\d{2}(?::\d{2})?)[\]\)]?$'
)

# Non-speaker metadata prefixes to ignore during dialogue extraction
NON_SPEAKER_PREFIXES = {
    "role", "market", "date", "topic", "project", "interviewer note", "note", "title", "expert"
}

# Speaker detection - name followed by colon
SPEAKER_PATTERN = re.compile(
    r'^([A-Z][A-Za-z\s\.\-\,\']+(?:Dr\.|Mr\.|Ms\.|Mrs\.|Prof\.)?[A-Za-z\s\.\-\,\']*)\s*:\s*$',
    re.MULTILINE,
)

# Simpler speaker pattern: "Name:" on a line, possibly with text after
SPEAKER_INLINE_PATTERN = re.compile(
    r'^([A-Z][A-Za-z\s\.\-\,\']{2,50}):\s*(.*)',
    re.MULTILINE,
)


@dataclass
class ParsedUtterance:
    """A single parsed utterance from a transcript."""
    speaker: str
    text: str
    timestamp_start: str | None = None
    timestamp_end: str | None = None
    sequence: int = 0


@dataclass
class ParsedTranscript:
    """Result of parsing a transcript file."""
    utterances: list[ParsedUtterance] = field(default_factory=list)
    detected_speakers: list[str] = field(default_factory=list)
    has_timestamps: bool = False
    warnings: list[str] = field(default_factory=list)


def parse_transcript(text: str) -> ParsedTranscript:
    """Parse transcript text into structured utterances.

    Args:
        text: Raw transcript text content

    Returns:
        ParsedTranscript with list of utterances

    Raises:
        ParsingError: If text cannot be parsed at all
    """
    if not text or not text.strip():
        raise ParsingError(
            message="Empty transcript",
            detail="Transcript file contains no text",
        )

    # Try different parsing strategies in order
    result = _parse_timestamp_range_format(text)
    if result and result.utterances:
        logger.info(
            f"Parsed {len(result.utterances)} utterances using timestamp-range format",
            extra={"operation": "transcript_parse"},
        )
        return result

    result = _parse_speaker_block_format(text)
    if result and result.utterances:
        logger.info(
            f"Parsed {len(result.utterances)} utterances using speaker-block format",
            extra={"operation": "transcript_parse"},
        )
        return result

    result = _parse_inline_speaker_format(text)
    if result and result.utterances:
        logger.info(
            f"Parsed {len(result.utterances)} utterances using inline-speaker format",
            extra={"operation": "transcript_parse"},
        )
        return result

    # Fallback: treat entire text as a single utterance
    logger.warning(
        "Could not detect structured format, using fallback",
        extra={"operation": "transcript_parse"},
    )
    result = ParsedTranscript(
        utterances=[
            ParsedUtterance(
                speaker="Unknown",
                text=text.strip(),
                sequence=0,
            )
        ],
        warnings=["Could not detect structured transcript format. Entire text treated as single utterance."],
    )
    return result


def _parse_timestamp_range_format(text: str) -> ParsedTranscript | None:
    """Parse format:
    00:12:31 - 00:12:46
    Dr. Emily Carter:
    "The hospital usually..."

    or variations like:
    00:12:31 - 00:12:46
    Speaker Name:
    Text content here
    """
    lines = text.split('\n')
    utterances: list[ParsedUtterance] = []
    speakers: set[str] = set()
    has_timestamps = False

    current_ts_start: str | None = None
    current_ts_end: str | None = None
    current_speaker: str | None = None
    current_text_lines: list[str] = []
    sequence = 0

    def flush():
        nonlocal sequence
        if current_speaker and current_text_lines:
            text_content = ' '.join(current_text_lines).strip()
            # Remove surrounding quotes
            text_content = text_content.strip('"').strip("'").strip('"').strip('"').strip()
            if text_content:
                utterances.append(ParsedUtterance(
                    speaker=current_speaker,
                    text=text_content,
                    timestamp_start=current_ts_start,
                    timestamp_end=current_ts_end,
                    sequence=sequence,
                ))
                sequence += 1

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for timestamp range
        ts_match = TIMESTAMP_RANGE_PATTERN.match(stripped)
        if ts_match:
            # Flush previous utterance
            flush()
            current_ts_start = ts_match.group(1)
            current_ts_end = ts_match.group(2)
            current_speaker = None
            current_text_lines = []
            has_timestamps = True
            continue

        # Check for single timestamp
        single_ts = SINGLE_TIMESTAMP_PATTERN.match(stripped)
        if single_ts:
            flush()
            current_ts_start = single_ts.group(1)
            current_ts_end = None
            current_speaker = None
            current_text_lines = []
            has_timestamps = True
            continue

        # Check for speaker line (name followed by colon, nothing else)
        speaker_match = re.match(r'^([A-Z][A-Za-z\s\.\-\,\']{2,60}):\s*$', stripped)
        if speaker_match:
            if current_speaker and current_text_lines:
                flush()
                # Keep timestamps if this speaker block had no timestamp
                if not has_timestamps:
                    current_ts_start = None
                    current_ts_end = None
            current_speaker = speaker_match.group(1).strip()
            speakers.add(current_speaker)
            current_text_lines = []
            continue

        # Otherwise it's text content
        if current_speaker is not None:
            current_text_lines.append(stripped)
        elif current_ts_start is not None:
            # We have a timestamp but no speaker identified yet
            # Check if this line is "Speaker: text"
            inline_match = re.match(r'^([A-Z][A-Za-z\s\.\-\,\']{2,50}):\s*(.+)', stripped)
            if inline_match:
                current_speaker = inline_match.group(1).strip()
                speakers.add(current_speaker)
                current_text_lines = [inline_match.group(2).strip()]
            else:
                current_speaker = "Unknown"
                current_text_lines.append(stripped)

    # Flush last utterance
    flush()

    if not utterances:
        return None

    return ParsedTranscript(
        utterances=utterances,
        detected_speakers=sorted(speakers),
        has_timestamps=has_timestamps,
    )


def _parse_speaker_block_format(text: str) -> ParsedTranscript | None:
    """Parse format where speakers are identified by 'Name:' on separate lines
    followed by their text."""
    lines = text.split('\n')
    utterances: list[ParsedUtterance] = []
    speakers: set[str] = set()
    has_timestamps = False

    current_speaker: str | None = None
    current_text_lines: list[str] = []
    current_ts_start: str | None = None
    current_ts_end: str | None = None
    sequence = 0

    def flush():
        nonlocal sequence
        if current_speaker and current_text_lines:
            text_content = ' '.join(current_text_lines).strip()
            text_content = text_content.strip('"').strip("'").strip('"').strip('"').strip()
            if text_content:
                utterances.append(ParsedUtterance(
                    speaker=current_speaker,
                    text=text_content,
                    timestamp_start=current_ts_start,
                    timestamp_end=current_ts_end,
                    sequence=sequence,
                ))
                sequence += 1

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for timestamp
        ts_match = TIMESTAMP_RANGE_PATTERN.match(stripped)
        if ts_match:
            current_ts_start = ts_match.group(1)
            current_ts_end = ts_match.group(2)
            has_timestamps = True
            continue

        single_ts = SINGLE_TIMESTAMP_PATTERN.match(stripped)
        if single_ts:
            current_ts_start = single_ts.group(1)
            current_ts_end = None
            has_timestamps = True
            continue

        # Check for speaker line
        speaker_match = re.match(r'^([A-Z][A-Za-z\s\.\-\,\']{2,60}):\s*$', stripped)
        if speaker_match:
            flush()
            current_speaker = speaker_match.group(1).strip()
            speakers.add(current_speaker)
            current_text_lines = []
            continue

        # Text content
        if current_speaker:
            current_text_lines.append(stripped)

    flush()

    if not utterances:
        return None

    return ParsedTranscript(
        utterances=utterances,
        detected_speakers=sorted(speakers),
        has_timestamps=has_timestamps,
    )


def _parse_inline_speaker_format(text: str) -> ParsedTranscript | None:
    """Parse format: 'Speaker Name: text content here'"""
    lines = text.split('\n')
    utterances: list[ParsedUtterance] = []
    speakers: set[str] = set()
    has_timestamps = False
    sequence = 0

    current_ts_start: str | None = None
    current_ts_end: str | None = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for timestamp
        ts_match = TIMESTAMP_RANGE_PATTERN.match(stripped)
        if ts_match:
            current_ts_start = ts_match.group(1)
            current_ts_end = ts_match.group(2)
            has_timestamps = True
            continue

        single_ts = SINGLE_TIMESTAMP_PATTERN.match(stripped)
        if single_ts:
            current_ts_start = single_ts.group(1)
            current_ts_end = None
            has_timestamps = True
            continue

        # Check for inline speaker
        inline_match = re.match(r'^([A-Z][A-Za-z\s\.\-\,\']{2,50}):\s*(.+)', stripped)
        if inline_match:
            speaker = inline_match.group(1).strip()
            if speaker.lower() in NON_SPEAKER_PREFIXES:
                continue
            text_content = inline_match.group(2).strip().strip('"').strip("'").strip('"').strip('"').strip()
            speakers.add(speaker)
            if text_content:
                utterances.append(ParsedUtterance(
                    speaker=speaker,
                    text=text_content,
                    timestamp_start=current_ts_start,
                    timestamp_end=current_ts_end,
                    sequence=sequence,
                ))
                sequence += 1
                current_ts_start = None
                current_ts_end = None

    if not utterances:
        return None

    return ParsedTranscript(
        utterances=utterances,
        detected_speakers=sorted(speakers),
        has_timestamps=has_timestamps,
    )
