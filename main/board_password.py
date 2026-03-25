"""
자유게시판 글 비밀번호: Django 기본 해시(PBKDF2 등) 저장 및 검증.
기존 평문 저장 데이터는 검증 시 자동으로 해시로 갱신한다.
"""

from __future__ import annotations

import hmac

from django.contrib.auth.hashers import check_password, identify_hasher, make_password


def hash_board_password(raw_password: str) -> str:
    return make_password(raw_password)


def is_password_hashed(stored: str) -> bool:
    if not stored:
        return False
    try:
        identify_hasher(stored)
        return True
    except ValueError:
        return False


def verify_board_password(raw_password: str, stored: str) -> bool:
    if not stored or raw_password is None:
        return False
    if not is_password_hashed(stored):
        return hmac.compare_digest(stored, raw_password)
    return check_password(raw_password, stored)


def upgrade_stored_password_if_legacy(post, raw_password: str) -> None:
    """평문으로 저장된 레코드를 한 번 해시로 바꾼다 (DB에만 반영)."""
    if is_password_hashed(post.password):
        return
    if not verify_board_password(raw_password, post.password):
        return
    post.password = hash_board_password(raw_password)
    post.save(update_fields=["password"])
