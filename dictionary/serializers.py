from .models import Dictionary
from base.serializers import BaseHyperlinkedModelSerializer


class DictionarySerializer(BaseHyperlinkedModelSerializer):
    class Meta(BaseHyperlinkedModelSerializer.Meta):
        model = Dictionary

    def create(self, validated_data):
        return Dictionary.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.save()
        return instance



