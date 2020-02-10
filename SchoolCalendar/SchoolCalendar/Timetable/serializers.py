from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer


# Serializers define the API representation.
class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

