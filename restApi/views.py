from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from restApi.models import WordsStats
from restApi.serializers import WordsSerializer


# @csrf_exempt
def word_list(request):
    """
    List all words, or create a new snippet.
    """
    if request.method == 'GET':
        words = WordsStats.objects.all()
        serializer = WordsSerializer(words, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = WordsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


# @csrf_exempt
def word_detail(request, r_word):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        word = WordsStats.objects.get(word=r_word)
    except WordsStats.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = WordsSerializer(word)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = WordsSerializer(word, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        word.delete()
        return HttpResponse(status=204)