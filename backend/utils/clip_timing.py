"""Clip boundary helpers: snap AI-picked clip windows to sentence boundaries."""
from typing import Any, Dict, List, Tuple

SENTENCE_END = (".", "?", "!", "…")


def _ends_sentence(text: str) -> bool:
    return text.strip().endswith(SENTENCE_END)


def snap_to_sentence_boundaries(
    start: float,
    end: float,
    lines: List[Dict[str, Any]],
    window: float = 2.0,
    min_duration: float = 0.0,
    max_duration: float = float("inf"),
) -> Tuple[float, float]:
    """Move start/end to the nearest transcript line boundary within `window` seconds.

    A clip should open at the start of a sentence and close at the end of one, never mid-word.
    Boundaries that coincide with sentence punctuation are preferred over plain line breaks.
    Each side is only moved if the clip stays within [min_duration, max_duration].
    """
    if not lines or end <= start:
        return start, end

    ordered = sorted(lines, key=lambda l: float(l.get("start", 0.0)))

    # Candidate starts: line starts; a line that follows a sentence end is a "strong" start.
    start_candidates = []
    for i, line in enumerate(ordered):
        ls = float(line.get("start", 0.0))
        if abs(ls - start) <= window:
            strong = i == 0 or _ends_sentence(str(ordered[i - 1].get("text", "")))
            start_candidates.append((0 if strong else 1, abs(ls - start), ls))

    # Candidate ends: line ends; a line ending in sentence punctuation is a "strong" end.
    end_candidates = []
    for line in ordered:
        le = float(line.get("end", float(line.get("start", 0.0)) + float(line.get("duration", 0.0))))
        if abs(le - end) <= window:
            strong = _ends_sentence(str(line.get("text", "")))
            end_candidates.append((0 if strong else 1, abs(le - end), le))

    new_start, new_end = start, end
    for _, _, candidate in sorted(start_candidates):
        if min_duration <= end - candidate <= max_duration:
            new_start = candidate
            break
    for _, _, candidate in sorted(end_candidates):
        if candidate > new_start and min_duration <= candidate - new_start <= max_duration:
            new_end = candidate
            break
    return round(new_start, 2), round(new_end, 2)
