import logging

logger = logging.getLogger(__name__)

class LoginTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/accounts/') and 'login_type' in request.GET:
            login_type = request.GET['login_type']
            request.session['login_type'] = login_type
            logger.debug(f"Middleware set login_type={login_type} for path={request.path}")
        response = self.get_response(request)
        return response