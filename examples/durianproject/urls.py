from django.conf.urls.defaults import patterns, url, include
from durian.urls import durian
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^durian/', durian.urls),
    url(r'^admin/', admin.site.urls),
    url(r"%s(?P<path>.*)$" % settings.MEDIA_URL[1:],
        "django.views.static.serve", {
        "document_root": settings.MEDIA_ROOT}),
)
