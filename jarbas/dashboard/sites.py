from functools import update_wrapper

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseForbidden
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect


class DummyUser(AnonymousUser):

    def has_module_perms(self, app_label):
        return app_label == 'core'

    def has_perm(self, permission, obj=None):
        return permission == 'core.change_reimbursement'


class DashboardSite(AdminSite):

    site_title = 'Dashboard'
    site_header = 'Jarbas Dashboard'
    index_title = 'Jarbas'

    def __init__(self):
        super().__init__('dashboard')
        self._actions, self._global_actions = {}, {}

    @staticmethod
    def valid_url(url):
        forbidden = (
            'auth',
            'login',
            'logout',
            'password',
            'add',
            'delete',
        )
        return all(label not in url.regex.pattern for label in forbidden)

    @property
    def urls(self):
        urls = filter(self.valid_url, self.get_urls())
        return list(urls), 'admin', self.name

    def has_permission(self, request):
        return request.method == 'GET'

    def admin_view(self, view, cacheable=False):
        def inner(request, *args, **kwargs):
            request.user = DummyUser()
            if not self.has_permission(request):
                return HttpResponseForbidden()
            return view(request, *args, **kwargs)

        if not cacheable:
            inner = never_cache(inner)

        if not getattr(view, 'csrf_exempt', False):
            inner = csrf_protect(inner)

        return update_wrapper(inner, view)


dashboard = DashboardSite()
