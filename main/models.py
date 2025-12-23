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
