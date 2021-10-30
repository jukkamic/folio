from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import json
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from blog.models import Post, Author
from blog.serializers import PostSerializer, AuthorSerializer

@csrf_exempt
@api_view(['GET', 'POST'])
def postApi(request):
    if (request.method == 'GET'):
        posts = Post.objects.all()
        post_serializer = PostSerializer(posts, many=True)
        return JsonResponse(data=json.dumps(post_serializer.data), safe=False)
    elif request.method=='POST':
        post_data = JSONParser().parse(request)
        post_serializer = PostSerializer(data=post_data)
        if post_serializer.is_valid():
            post_serializer.save()
            return JsonResponse("Added successfully!", safe=False)
        return JsonResponse("Failed to add.", safe=False)
