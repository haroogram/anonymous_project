from django.db import models
from django.urls import reverse


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
        max_length=128,
        verbose_name="수정/삭제 비밀번호",
        help_text="게시글 수정/삭제 시 사용할 비밀번호",
    )
    anonymous_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        verbose_name="익명 ID",
        help_text="쿠키 기반 익명 사용자 식별자",
    )
    content = models.TextField(verbose_name="내용")
    # 향후 파일 업로드를 위한 확장 포인트 (별도 File 모델 또는 GenericRelation 등으로 확장 예정)
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