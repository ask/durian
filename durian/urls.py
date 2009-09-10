from django.conf.urls.defaults import patterns, url, include
from durian import views


urlpatterns = patterns("",
    url(r'^debug/', views.debug, name="debug")
)
