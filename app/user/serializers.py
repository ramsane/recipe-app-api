from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

from django.utils.translation import ugettext as _


# Create a new serializer called User serializer, we are going to inherit from
# serilaizer.ModelSerializer. It does some tasks like creating and retreiving
# from the database, conversion from database results to Json and vice versa.
class UserSerializer(serializers.ModelSerializer):
    """Seriaizers for the users object"""

    # add Meta class
    class Meta:
        # specify the model that we want to base our modelserializer from
        model = get_user_model()
        # spedify the fields that we want to include in the serializer
        # These are the fields that are going to convert to and from Json,
        # when we make our http post. Basically, the fields that we want to
        # make accessible in API either to read or write.
        fields = ('email', 'password', 'name')
        # extra keyword args : it allows us to configure few extra settings in
        # our model serializer. We use this to ensure that the password is
        # WRITE_ONLY( to the database), and the minumum password length is
        # 5 characters
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authnetication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input-type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        # get the attributes from attrs atribute
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        # if authentication fails
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
