import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone


def board_attachment_upload_to(instance: "BoardAttachment", filename: str) -> str:
    """게시글별 하위 경로 + UUID 로 저장 경로 충돌 방지."""
    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower()
    post_id = instance.post_id or "pending"
    now = timezone.now()
    return f"board/{now:%Y}/{now:%m}/{post_id}/{uuid.uuid4().hex}{ext}"


class Category(models.Model):
    """카테고리 모델"""
    name = models.CharField(max_length=100, verbose_name='카테고리명')
    slug = models.SlugField(unique=True, verbose_name='슬러그')
    description = models.TextField(blank=True, verbose_name='설명')
    order = models.PositiveIntegerField(default=0, verbose_name='순서')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tutorial', kwargs={'category': self.slug})


class Topic(models.Model):
    """주제 모델 - Category의 하위 서브카테고리"""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='topics',
        verbose_name='카테고리'
    )
    title = models.CharField(max_length=200, verbose_name='제목')
    slug = models.SlugField(verbose_name='슬러그')
    content = models.TextField(blank=True, verbose_name='내용')
    order = models.PositiveIntegerField(default=0, verbose_name='순서')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '주제'
        verbose_name_plural = '주제'
        ordering = ['order', 'title']
        unique_together = [['category', 'slug']]  # 같은 카테고리 내에서 slug는 유일해야 함

    def __str__(self):
        return f"{self.category.name} - {self.title}"

    def get_absolute_url(self):
        return reverse('topic_detail', kwargs={
            'category': self.category.slug,
            'topic': self.slug
        })


class VisitorStats(models.Model):
    """일별 접속자 수 통계 모델"""
    date = models.DateField(unique=True, verbose_name='날짜', db_index=True)
    visitor_count = models.PositiveIntegerField(default=0, verbose_name='접속자 수')
    unique_visitor_count = models.PositiveIntegerField(default=0, verbose_name='고유 접속자 수')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '접속자 통계'
        verbose_name_plural = '접속자 통계'
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.visitor_count}명"


class BoardPost(models.Model):
    """자유게시판 게시글"""

    title = models.CharField(max_length=200, verbose_name="제목")
    author_name = models.CharField(
        max_length=50,
        verbose_name="작성자명",
        help_text="닉네임 또는 이름",
    )
    password = models.CharField(
        max_length=256,
        verbose_name="수정/삭제 비밀번호",
        help_text="게시글 수정/삭제 시 사용할 비밀번호 (해시 저장)",
    )
    anonymous_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        verbose_name="익명 ID",
        help_text="쿠키 기반 익명 사용자 식별자",
    )
    author_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="board_posts",
        verbose_name="로그인 작성자",
    )
    content = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    class Meta:
        verbose_name = "자유게시판 글"
        verbose_name_plural = "자유게시판 글"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("board_detail", kwargs={"pk": self.pk})

    def get_anonymous_nickname(self) -> str:
        """
        쿠키 기반 익명 ID + IP 마스킹을 이용한 닉네임 표시.
        예: #A1B2(112.221.xxx.xxx)
        """
        code = f"#{self.anonymous_id[:4].upper()}" if self.anonymous_id else "익명"
        ip_part = self.author_name or ""
        # author_name 은 이미 익명(112.221.xxx.xxx) 형태이므로 괄호 안 내용만 추출
        if ip_part.startswith("익명(") and ip_part.endswith(")"):
            ip_inner = ip_part[3:-1]
            if ip_inner:
                return f"{code}({ip_inner})"
        return code

    def get_display_author(self) -> str:
        if self.author_user_id:
            return self.author_user.get_username()
        return self.get_anonymous_nickname()


class BoardAttachment(models.Model):
    """자유게시판 첨부파일 (게시글당 다중 파일)."""

    post = models.ForeignKey(
        BoardPost,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="게시글",
    )
    file = models.FileField(
        upload_to=board_attachment_upload_to,
        max_length=500,
        verbose_name="파일",
    )
    original_name = models.CharField(
        max_length=255,
        verbose_name="원본 파일명",
        help_text="다운로드 시 표시할 이름",
    )
    size = models.PositiveIntegerField(default=0, verbose_name="크기(바이트)")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="업로드 시각")

    class Meta:
        verbose_name = "자유게시판 첨부"
        verbose_name_plural = "자유게시판 첨부"
        ordering = ["uploaded_at", "id"]

    def __str__(self):
        return self.original_name or str(self.file)


@receiver(pre_delete, sender=BoardAttachment)
def _delete_board_attachment_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)


class BoardComment(models.Model):
    """자유게시판 댓글 (대댓글은 parent 가 최상위 댓글인 경우만 허용)."""

    post = models.ForeignKey(
        BoardPost,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="게시글",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="상위 댓글",
    )
    author_name = models.CharField(
        max_length=50,
        verbose_name="작성자 표시",
        help_text="IP 마스킹 등 서버에서 설정",
    )
    anonymous_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        verbose_name="익명 ID",
    )
    author_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="board_comments",
        verbose_name="로그인 작성자",
    )
    content = models.TextField(max_length=2000, verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    class Meta:
        verbose_name = "자유게시판 댓글"
        verbose_name_plural = "자유게시판 댓글"
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["post", "parent", "is_deleted", "created_at"]),
        ]

    def __str__(self):
        return f"{self.post_id}: {self.content[:40]}"

    def get_anonymous_nickname(self) -> str:
        code = f"#{self.anonymous_id[:4].upper()}" if self.anonymous_id else "익명"
        ip_part = self.author_name or ""
        if ip_part.startswith("익명(") and ip_part.endswith(")"):
            ip_inner = ip_part[3:-1]
            if ip_inner:
                return f"{code}({ip_inner})"
        return code

    def get_display_author(self) -> str:
        if self.author_user_id:
            return self.author_user.get_username()
        return self.get_anonymous_nickname()


class BoardPostSubscriber(models.Model):
    """로그인 사용자가 댓글을 단 글에 대해 이후 새 댓글 알림을 받기 위한 구독."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="board_post_subscriptions",
        verbose_name="사용자",
    )
    post = models.ForeignKey(
        BoardPost,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="게시글",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="구독일")

    class Meta:
        verbose_name = "게시글 알림 구독"
        verbose_name_plural = "게시글 알림 구독"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="uniq_board_post_subscriber_user_post",
            ),
        ]


class BoardNotification(models.Model):
    """로그인 사용자용 자유게시판 알림 (구독 글의 새 댓글 / 내 댓글에 답글)."""

    class Kind(models.TextChoices):
        THREAD_COMMENT = "thread_comment", "게시글 새 댓글"
        REPLY = "reply", "내 댓글에 답글"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="board_notifications",
        verbose_name="수신자",
    )
    post = models.ForeignKey(
        BoardPost,
        on_delete=models.CASCADE,
        related_name="board_notifications",
        verbose_name="게시글",
    )
    comment = models.ForeignKey(
        BoardComment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="관련 댓글",
    )
    kind = models.CharField(
        max_length=32,
        choices=Kind.choices,
        verbose_name="종류",
    )
    summary = models.CharField(max_length=200, verbose_name="요약")
    is_read = models.BooleanField(default=False, verbose_name="읽음")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")

    class Meta:
        verbose_name = "자유게시판 알림"
        verbose_name_plural = "자유게시판 알림"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
        ]