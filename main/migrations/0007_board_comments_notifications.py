# 댓글/대댓글 및 로그인 사용자 알림

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_alter_boardpost_password_hash_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BoardComment",
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
                    "author_name",
                    models.CharField(
                        help_text="IP 마스킹 등 서버에서 설정",
                        max_length=50,
                        verbose_name="작성자 표시",
                    ),
                ),
                (
                    "anonymous_id",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=64,
                        verbose_name="익명 ID",
                    ),
                ),
                (
                    "content",
                    models.TextField(max_length=2000, verbose_name="내용"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="작성일"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="수정일"),
                ),
                (
                    "is_deleted",
                    models.BooleanField(default=False, verbose_name="삭제 여부"),
                ),
                (
                    "author_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="board_comments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="로그인 작성자",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="main.boardcomment",
                        verbose_name="상위 댓글",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="main.boardpost",
                        verbose_name="게시글",
                    ),
                ),
            ],
            options={
                "verbose_name": "자유게시판 댓글",
                "verbose_name_plural": "자유게시판 댓글",
                "ordering": ["created_at", "id"],
            },
        ),
        migrations.CreateModel(
            name="BoardPostSubscriber",
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
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="구독일"),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscribers",
                        to="main.boardpost",
                        verbose_name="게시글",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="board_post_subscriptions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "게시글 알림 구독",
                "verbose_name_plural": "게시글 알림 구독",
            },
        ),
        migrations.CreateModel(
            name="BoardNotification",
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
                    "kind",
                    models.CharField(
                        choices=[
                            ("thread_comment", "게시글 새 댓글"),
                            ("reply", "내 댓글에 답글"),
                        ],
                        max_length=32,
                        verbose_name="종류",
                    ),
                ),
                (
                    "summary",
                    models.CharField(max_length=200, verbose_name="요약"),
                ),
                (
                    "is_read",
                    models.BooleanField(default=False, verbose_name="읽음"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성일"),
                ),
                (
                    "comment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="main.boardcomment",
                        verbose_name="관련 댓글",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="board_notifications",
                        to="main.boardpost",
                        verbose_name="게시글",
                    ),
                ),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="board_notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="수신자",
                    ),
                ),
            ],
            options={
                "verbose_name": "자유게시판 알림",
                "verbose_name_plural": "자유게시판 알림",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="boardpostsubscriber",
            constraint=models.UniqueConstraint(
                fields=("user", "post"),
                name="uniq_board_post_subscriber_user_post",
            ),
        ),
        migrations.AddIndex(
            model_name="boardcomment",
            index=models.Index(
                fields=["post", "parent", "is_deleted", "created_at"],
                name="main_bc_post_parent_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="boardnotification",
            index=models.Index(
                fields=["recipient", "is_read"],
                name="main_bn_recipient_read_idx",
            ),
        ),
    ]
