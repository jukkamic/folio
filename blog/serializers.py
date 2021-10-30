from rest_framework import serializers
from blog.models import Post, Author

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('author', 'title', 'content')

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('name', 'user')
