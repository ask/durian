from django.conf.urls.defaults import patterns, url, include
from durian.urls import durian

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^durian/', durian.urls),
)
