"""
자유게시판 첨부파일 검증 (크기, 개수, 확장자).
"""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError


def _allowed_extensions() -> frozenset[str]:
    return frozenset(
        ext.lower().lstrip(".")
        for ext in getattr(
            settings,
            "BOARD_ATTACHMENT_ALLOWED_EXTENSIONS",
            (),
        )
    )


def validate_board_uploaded_files(
    files: list,
    *,
    current_count: int = 0,
) -> None:
    """
    request.FILES.getlist(...) 결과에 대해 일괄 검증.
    실패 시 ValidationError (메시지는 사용자에게 표시 가능한 한글).
    """
    if not files:
        return

    max_count = int(getattr(settings, "BOARD_ATTACHMENT_MAX_COUNT", 5))
    max_bytes = int(getattr(settings, "BOARD_ATTACHMENT_MAX_BYTES", 10 * 1024 * 1024))
    allowed = _allowed_extensions()

    if current_count + len(files) > max_count:
        raise ValidationError(
            f"첨부파일은 게시글당 최대 {max_count}개까지 업로드할 수 있습니다."
        )

    for f in files:
        name = getattr(f, "name", "") or ""
        ext = Path(name).suffix.lower().lstrip(".")
        if ext not in allowed:
            sample = ", ".join(f".{e}" for e in sorted(allowed))
            raise ValidationError(
                f"허용되지 않는 파일 형식입니다: .{ext or '(확장자 없음)'} "
                f"(허용: {sample})"
            )
        size = getattr(f, "size", 0) or 0
        if size > max_bytes:
            mb = max_bytes / (1024 * 1024)
            raise ValidationError(
                f"파일 크기는 각각 {mb:.0f}MB를 넘을 수 없습니다."
            )
