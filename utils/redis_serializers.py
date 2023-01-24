from django.core import serializers

from utils.json_encoder import JSONEncoder


class DjangoModelSerializer:
    @classmethod
    def serialize(cls, instance):
        # Django serializers need Queryset or list to serialize
        # convert the instance to [instance]
        return serializers.serialize("json", [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        # need .object to convert to the instance
        return list(serializers.deserialize("json", serialized_data))[0].object
