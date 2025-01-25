from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
       @wraps(view_func)
       def _wrapped_view(request, *args, **kwargs):
           if hasattr(request.user, 'is_admin') and request.user.is_admin:
               return view_func(request, *args, **kwargs)
           else:
               messages.error(request, 'You do not have permission to access this page.')
               return redirect('homepage')  # or wherever you want to redirect non-admin users
       return _wrapped_view