from django.contrib import admin

from .models import BoardAttachment, BoardPost, Category, Topic, VisitorStats


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
    list_display = ['title', 'author_name', 'is_deleted', 'created_at', 'updated_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['title', 'content', 'author_name', 'anonymous_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [BoardAttachmentInline]
