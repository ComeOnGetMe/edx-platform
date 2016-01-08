""" Common Authentication Handlers used across projects. """
from rest_framework.authentication import SessionAuthentication
from rest_framework import exceptions as drf_exceptions
from rest_framework_oauth.authentication import OAuth2Authentication
from .exceptions import AuthenticationFailed
from rest_framework_oauth.compat import oauth2_provider, provider_now


class SessionAuthenticationAllowInactiveUser(SessionAuthentication):
    """Ensure that the user is logged in, but do not require the account to be active.

    We use this in the special case that a user has created an account,
    but has not yet activated it.  We still want to allow the user to
    enroll in courses, so we remove the usual restriction
    on session authentication that requires an active account.

    You should use this authentication class ONLY for end-points that
    it's safe for an un-activated user to access.  For example,
    we can allow a user to update his/her own enrollments without
    activating an account.

    """
    def authenticate(self, request):
        """Authenticate the user, requiring a logged-in account and CSRF.

        This is exactly the same as the `SessionAuthentication` implementation,
        with the `user.is_active` check removed.

        Args:
            request (HttpRequest)

        Returns:
            Tuple of `(user, token)`

        Raises:
            PermissionDenied: The CSRF token check failed.

        """
        # Get the underlying HttpRequest object
        request = request._request  # pylint: disable=protected-access
        user = getattr(request, 'user', None)

        # Unauthenticated, CSRF validation not required
        # This is where regular `SessionAuthentication` checks that the user is active.
        # We have removed that check in this implementation.
        # But we added a check to prevent anonymous users since we require a logged-in account.
        if not user or user.is_anonymous():
            return None

        self.enforce_csrf(request)

        # CSRF passed with authenticated user
        return (user, None)


class OAuth2AuthenticationAllowInactiveUser(OAuth2Authentication):
    """
    This is a temporary workaround while the is_active field on the user is coupled
    with whether or not the user has verified ownership of their claimed email address.
    Once is_active is decoupled from verified_email, we will no longer need this
    class override.

    But until then, this authentication class ensures that the user is logged in,
    but does not require that their account "is_active".

    This class can be used for an OAuth2-accessible endpoint that allows users to access
    that endpoint without having their email verified.  For example, this is used
    for mobile endpoints.
    """

    def authenticate(self, *args, **kwargs):
        """
        Returns two-tuple of (user, token) if access token authentication
        succeeds, raises an AuthenticationFailed (HTTP 401) if authentication
        fails or None if the user did not try to authenticate using an access
        token.

        Overrides base class implementation to return edX-style error
        responses.
        """

        try:
            return super(OAuth2AuthenticationAllowInactiveUser, self).authenticate(*args, **kwargs)
        except drf_exceptions.AuthenticationFailed as exc:
            if 'No credentials provided' in exc.detail:
                error_code = u'token_not_provided'
            elif 'Token string should not' in exc.detail:
                error_code = u'token_nonexistent'
            else:
                error_code = u'token_error'
            raise AuthenticationFailed({
                u'error_code': error_code,
                u'developer_message': exc.detail
            })

    def authenticate_credentials(self, request, access_token):
        """
        Authenticate the request, given the access token.
        Overrides base class implementation to discard failure if user is inactive.
        """
        token_qs = oauth2_provider.oauth2.models.AccessToken.objects.select_related('user')
        token = token_qs.filter(token=access_token).order_by('-expires').first()
        if not token:
            raise AuthenticationFailed({
                u'error_code': u'token_nonexistent',
                u'developer_message': u'The provided access token does not match any valid tokens'
            })
        # provider_now switches to timezone aware datetime when
        # the oauth2_provider version supports to it.
        elif token.expires < provider_now():
            raise AuthenticationFailed({
                u'error_code': u'token_expired',
                u'developer_message': u'The provided access token has expired and is no longer valid',
            })
        else:
            return token.user, token
