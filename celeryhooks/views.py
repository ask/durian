import sys
from django.http import HttpResponse
from anyjson import deserialize


def debug(request):
    sys.stderr.write(str(request.get_full_path()) + "\n")
    sys.stderr.write(str(request.raw_post_data) + "\n")
    sys.stderr.write(str(request.POST) + "\n")
    sys.stderr.write(str(deserialize(request.raw_post_data)) + "\n")
    return HttpResponse("Thanks!")
