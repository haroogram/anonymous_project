# Generated manually for BoardAttachment

import django.db.models.deletion
from django.db import migrations, models

from ..models import board_attachment_upload_to


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_boardpost_anonymous_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="BoardAttachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        max_length=500,
                        upload_to=board_attachment_upload_to,
                        verbose_name="파일",
                    ),
                ),
                (
                    "original_name",
                    models.CharField(
                        help_text="다운로드 시 표시할 이름",
                        max_length=255,
                        verbose_name="원본 파일명",
                    ),
                ),
                (
                    "size",
                    models.PositiveIntegerField(default=0, verbose_name="크기(바이트)"),
                ),
                (
                    "uploaded_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="업로드 시각"),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="main.boardpost",
                        verbose_name="게시글",
                    ),
                ),
            ],
            options={
                "verbose_name": "자유게시판 첨부",
                "verbose_name_plural": "자유게시판 첨부",
                "ordering": ["uploaded_at", "id"],
            },
        ),
    ]
