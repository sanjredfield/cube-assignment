import json

from django.contrib.auth import authenticate, login, logout
from django.forms import CharField, Form, ModelForm, PasswordInput
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from rest_framework import mixins, permissions, serializers, viewsets

from . import check_post_request
from .subscription import SubscriptionSerializer
from ..models import UserProfile
from ..multichain import MultichainRPC
from ..tasks import send_registration_email
from ..util import confirm_token


class UserForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password')

    email = CharField(max_length=75, required=True)


class LoginForm(Form):
    username = CharField()
    password = CharField(widget=PasswordInput())


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    subscription = SubscriptionSerializer()

    class Meta:
        model = UserProfile
        fields = (
            'url', 'id', 'username', 'valid_subscription', 'email_confirmed', 'subscription'
        )


class UserProfileViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    API endpoint that allows own user to be viewed.
    """
    queryset = UserProfile.objects.all().order_by('-date_joined')
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)


class UserSessionViews(object):

    multichain_rpc = MultichainRPC()

    @check_post_request
    def add_user(self, request):
        form = UserForm(json.loads(request.body))
        if form.is_valid():
            chain_address = self.multichain_rpc.create_chain_address()
            form.cleaned_data['chain_address'] = chain_address
            UserProfile.objects.create_user(**form.cleaned_data)
            new_user = authenticate(**form.cleaned_data)
            login(request, new_user)
            send_registration_email.delay(form.cleaned_data['email'])
            return JsonResponse({'result': 'success'})
        form_errors = json.loads(form.errors.as_json())
        return JsonResponse({'result': 'failure', 'errors': form_errors})

    @check_post_request
    def login(self, request):
        form = LoginForm(json.loads(request.body))
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid form data')

        user = authenticate(**form.cleaned_data)
        if user is not None:
            if user.is_active:
                login(request, user)
                return JsonResponse({'result': 'success'})
            return JsonResponse({'result': 'inactive'})
        return JsonResponse({'result': 'failure'})

    def confirm_email(self, request):
        try:
            print request.GET.get('token')
            email = confirm_token(request.GET.get('token'))
        except:
            return HttpResponseBadRequest('Invalid confirmation token!')

        user = UserProfile.objects.get(email=email)
        user.email_confirmed = True
        user.save()
        return HttpResponseRedirect('/')

    def logout(self, request):
        logout(request)
        return JsonResponse({'result': 'success'})
