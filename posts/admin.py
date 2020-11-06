from django.contrib import admin

from .models import Post, Group, Follow


class PostAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'text',
        'group',
        'pub_date',
        'author'
    )
    search_fields = (
        'text',
    )
    list_filter = (
        'pub_date',
    )
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description'
    )
    search_fields = (
        'title',
    )
    empty_value_display = "-пусто-"
    prepopulated_fields = {"slug": ("title",)}


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author',
    )
    search_fields = (
        'author',
    )
    empty_value_display = "-пусто-"


admin.site.register(Follow, FollowAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
