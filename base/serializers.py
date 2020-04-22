from rest_framework import serializers


class BaseHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    def create(self, validated_data):
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if isinstance(validated_data, dict) and len(validated_data) > 0:
            keys = list(validated_data)
            for key in keys:
                if hasattr(instance, key):
                    setattr(instance, key, validated_data[key])
        instance.save()
        return instance

    class Meta:
        fields = '__all__'
        read_only_fields = ('created_by', 'created_time', 'modified_by', 'modified_time', 'deleted',
                            'owner', 'pyr_guid')


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ('created_by', 'created_time')
