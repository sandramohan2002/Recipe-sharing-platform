from .models import CustomUser

class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
           request.user = None
           user_id = request.session.get('user_id')
           if user_id:
               try:
                   user = CustomUser.objects.get(id=user_id)
                   request.user = user
                   request.user.is_admin = request.session.get('is_admin', False)
               except CustomUser.DoesNotExist:
                   pass
           return self.get_response(request)