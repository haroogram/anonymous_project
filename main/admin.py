from django.contrib import admin
from .models import Category, Topic


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
