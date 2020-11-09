from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from pprint import pprint
import requests


@csrf_exempt
def webhook(request):
    response = MessagingResponse()
    pprint(request.POST)
    if request.method == "POST":
        message = request.POST.get("Body")
        print({'text': message})
        rasa_response = requests.post("http://localhost:5005/model/parse", json={'text': message})
        pprint(rasa_response.text)
        response.message('You said: ' + message)
    return HttpResponse(response.to_xml(), content_type='text/xml')