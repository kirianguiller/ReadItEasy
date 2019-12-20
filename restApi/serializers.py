from rest_framework import serializers
from restApi.models import WordsStats


class WordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordsStats
        fields = ['word', 'freq']