from django.conf.urls.defaults import patterns, url, include
from durian import views


class DurianSite(object):
    namespace = "durian"
    app_name = "durian"

    def __init__(self, namespace=None, app_name=None):
        self.namespace = namespace or self.namespace
        self.app_name = app_name or self.app_name

    @property
    def urlpatterns(self):
        return patterns("",
            url(r'^select/', views.select, name="select"),
            url(r'^create/', views.create, name="create"),
            url(r'^debug/', views.debug, name="debug"),
        )

    @property
    def urls(self):
        return (self.urlpatterns, "durian", "durian")


durian = DurianSite()
urlpatterns = durian.urlpatterns
