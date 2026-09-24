"""Tests for guide and transcript parsers."""
import pytest
from app.parsers.guide_parser import extract_guide_text
from app.parsers.transcript_parser import parse_transcript, ParsedUtterance
from app.core.exceptions import ParsingError


def test_guide_text_extraction():
    sample_text = """
    # Interview Guide: Surgical Robotics Adoption
    
    1. What are the key criteria when evaluating a robotic surgery platform?
    2. How does the procurement process typically unfold in your institution?
    3. What reimbursement hurdles have you encountered?
    """
    extracted = extract_guide_text(sample_text.encode("utf-8"), "interview_guide.txt")
    assert "Surgical Robotics Adoption" in extracted
    assert "procurement process" in extracted


def test_transcript_parser_timestamp_range_format():
    sample_transcript = """
00:01:15 - 00:01:45
Dr. Emily Carter:
"We started evaluating surgical robotics back in 2022. The initial hurdle was definitely capital outlay."

00:01:50 - 00:02:15
Interviewer:
"What about surgeon training times?"

00:02:20 - 00:03:00
Dr. Emily Carter:
"Surgeon training was surprisingly swift, taking roughly two weeks of intensive simulator work."
"""
    result = parse_transcript(sample_transcript)
    assert len(result.utterances) == 3
    assert result.has_timestamps is True

    u1 = result.utterances[0]
    assert u1.speaker == "Dr. Emily Carter"
    assert u1.timestamp_start == "00:01:15"
    assert u1.timestamp_end == "00:01:45"
    assert "capital outlay" in u1.text
    assert u1.sequence == 0

    u2 = result.utterances[1]
    assert u2.speaker == "Interviewer"
    assert u2.timestamp_start == "00:01:50"
    assert u2.timestamp_end == "00:02:15"
    assert u2.sequence == 1

    u3 = result.utterances[2]
    assert u3.speaker == "Dr. Emily Carter"
    assert u3.timestamp_start == "00:02:20"
    assert u3.timestamp_end == "00:03:00"
    assert "simulator work" in u3.text


def test_transcript_parser_inline_speaker_format():
    sample_transcript = """
Dr. Klaus Weber: In Germany, the Statutory Health Insurance negotiation is the primary bottleneck.
Interviewer: How long does that negotiation usually take?
Dr. Klaus Weber: Typically between six to nine months depending on clinical efficacy data.
"""
    result = parse_transcript(sample_transcript)
    assert len(result.utterances) == 3
    assert result.utterances[0].speaker == "Dr. Klaus Weber"
    assert "Statutory Health Insurance" in result.utterances[0].text
    assert result.utterances[1].speaker == "Interviewer"
    assert result.utterances[2].speaker == "Dr. Klaus Weber"


def test_transcript_parser_empty_error():
    with pytest.raises(ParsingError):
        parse_transcript("   \n\n  ")
