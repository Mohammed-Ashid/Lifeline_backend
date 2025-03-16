from django.contrib import admin
from .models import Person, Feed, Interaction  # Updated import from User to Person

@admin.register(Person)  # Updated to Person
class PersonAdmin(admin.ModelAdmin):  # Updated class name
    list_display = ('userId', 'userName', 'role', 'status', 'createdDate', 'updatedDate')
    list_filter = ('role', 'status')
    search_fields = ('userName', 'role')
    ordering = ('-createdDate',)

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'type', 'category', 'urgency', 'status', 'user', 'time_posted','date_posted', 'updated')
    list_filter = ('type', 'urgency', 'status', 'category')
    search_fields = ('title', 'content', 'user__userName', 'location')  # Updated to user__userName
    ordering = ('-date_posted',)

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'feed', 'likes', 'shares', 'comments_summary')
    list_filter = ('feed',)
    search_fields = ('feed__title',)
    ordering = ('-id',)

    def comments_summary(self, obj):
        return obj.comments[:50] + "..." if obj.comments and len(obj.comments) > 50 else obj.comments

    comments_summary.short_description = "Comments"
