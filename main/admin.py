from django import forms
from django.contrib import admin

from .board_password import hash_board_password
from .models import BoardAttachment, BoardPost, Category, Topic, VisitorStats


class BoardPostAdminForm(forms.ModelForm):
    """관리자에서 비밀번호는 해시로 저장. 수정 시 비워두면 기존 값 유지."""

    class Meta:
        model = BoardPost
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].widget = forms.PasswordInput(render_value=False)
        if self.instance and self.instance.pk:
            self.fields["password"].required = False
            self.fields["password"].help_text = "변경할 때만 입력하세요. 비워두면 기존 비밀번호를 유지합니다."

    def save(self, commit=True):
        instance = super().save(commit=False)
        pwd = (self.cleaned_data.get("password") or "").strip()
        if pwd:
            instance.password = hash_board_password(pwd)
        elif instance.pk:
            instance.password = BoardPost.objects.get(pk=instance.pk).password
        if commit:
            instance.save()
        return instance


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'slug', 'order', 'created_at']
    list_filter = ['category', 'created_at', 'updated_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['category', 'order', 'title']
    raw_id_fields = ['category']


@admin.register(VisitorStats)
class VisitorStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'visitor_count', 'unique_visitor_count', 'created_at', 'updated_at']
    list_filter = ['date', 'created_at']
    search_fields = ['date']
    ordering = ['-date']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']


class BoardAttachmentInline(admin.TabularInline):
    model = BoardAttachment
    extra = 0
    readonly_fields = ['uploaded_at', 'size']


@admin.register(BoardPost)
class BoardPostAdmin(admin.ModelAdmin):
    form = BoardPostAdminForm
    list_display = ['title', 'author_name', 'is_deleted', 'created_at', 'updated_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['title', 'content', 'author_name', 'anonymous_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [BoardAttachmentInline]
