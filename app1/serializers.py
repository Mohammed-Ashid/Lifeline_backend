from rest_framework import serializers
from .models import Feed

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ['id', 'type', 'category', 'group', 'urgency', 'user', 'location', 'title', 'content', 'status', 'time_posted', 'date_posted', 'updated']
        read_only_fields = ['id', 'time_posted', 'date_posted', 'updated']



from rest_framework import serializers
from .models import Feed

class FeedSerializerPending(serializers.ModelSerializer):
    # Customize the user field to include userName and status
    user = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = [
            'id', 'type', 'category', 'group', 'urgency', 'user', 
            'time_posted', 'location', 'title', 'content', 'status', 
            'date_posted', 'updated'
        ]
        read_only_fields = ['id', 'time_posted', 'date_posted', 'updated']

    def get_user(self, obj):
        # Return a dictionary with userId, userName, and status from the Person model
        return {
            'userId': obj.user.userId,
            'userName': obj.user.userName,
            'status': obj.user.status
        }
    

# app1/serializers.py
# app1/serializers.py
from rest_framework import serializers
from .models import Person

class PersonSerializer(serializers.ModelSerializer):
    idProof = serializers.FileField(use_url=True, required=False)  # Returns URL to the file

    class Meta:
        model = Person
        fields = ['userId', 'userName', 'role', 'status', 'createdDate', 'updatedDate', 'idProof']
        # Excluded 'password' for security