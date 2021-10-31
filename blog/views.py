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
def postsApi(request):
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

@csrf_exempt
@api_view(['GET'])
def getLatest(request, number):
    try:
        resp = []
        posts = Post.objects.order_by('-created_on')[:number]
        for p in posts:
            resp.append({"id": p.id, "author": p.author.name, "title": p.title, "content": p.content})
        return JsonResponse(data=json.dumps(resp), safe=False)
    except Exception as e:
        print(e)
        return JsonResponse(data={"error": "500"}, status=500, safe=False)
    
@csrf_exempt
@api_view(['GET', 'DELETE'])
def getPost(request, id):
    try:
        if (request.method == 'GET'):
            p = Post.objects.get(id=id)
            resp = {"id": p.id, "author": p.author.name, "title": p.title, "content": p.content}
            return JsonResponse(data=json.dumps(resp), safe=False)
        elif (request.method == 'DELETE'):
            p = Post.objects.get(id=id)
            p.delete()
            return JsonResponse(data={"message": "Post id " + str(id) + " deleted successfully"}, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse(data=json.dumps(e), status=500, safe=False)
