import re

from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import activate
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.EXCLUDED_URLS = [
            re.compile(r"^/social-auth/"),
            re.compile(r"^/users/login/"),
            re.compile(r"^/users/register/"),
            re.compile(r"^/static/"),
            re.compile(r"^/media/"),
        ]

    def __call__(self, request):
        if not request.user.is_authenticated:
            for pattern in self.EXCLUDED_URLS:
                if pattern.match(request.path):
                    return self.get_response(request)

            if request.path == settings.LOGIN_URL:
                return self.get_response(request)

            return redirect(settings.LOGIN_URL)

        return self.get_response(request)


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            language = getattr(request.user, "language", "en")
            activate(language)
            request.session["django_language"] = language

        response = self.get_response(request)
        return response


class ThemeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            request.session["theme"] = request.user.theme
        else:
            request.session["theme"] = "light"