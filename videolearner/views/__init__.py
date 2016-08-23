from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import permissions


@ensure_csrf_cookie
def index(request):
    return render(request, 'videolearner/index.html')


def check_post_request(func):
    def func_wrapper(obj, request):
        if request.method != "POST":
            return HttpResponseBadRequest("POST requests only!")
        if 'application/json' not in request.META['CONTENT_TYPE']:
            return HttpResponseBadRequest("Only JSON accepted!")
        return func(obj, request)
    return func_wrapper


def check_authenticated_and_confirmed(func):
    def func_wrapper(obj, request):
        if request.user.is_authenticated() and request.user.email_confirmed:
            return func(obj, request)
        return HttpResponseForbidden("You must be logged in to view this!")
    return func_wrapper


class IsAuthenticatedAndRegistered(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        parent = super(IsAuthenticatedAndRegistered, self)
        user = request.user
        return parent.has_permission(request, view) and user.email_confirmed
