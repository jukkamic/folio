from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

request_times = {}

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def getNews(request, kind, filter):
    print("Sending request to cryptopanic.")
    payload = {
                "auth_token": settings.CRYPTOPANIC_AUTH,
                "public": "true",
            }
    if kind != "all":
        payload["kind"] = kind
    if filter != "all":
        payload["filter"] = filter

    try:
        res = requests.get("https://cryptopanic.com/api/v1/posts/", params=payload)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception("Error fetching news.")

    if res.status_code == requests.codes.ok:
        return JsonResponse(data=res.json(), status=res.status_code, safe=False)
    else:
        print(res.request.url)
        res.raise_for_status()

