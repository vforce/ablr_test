from time import sleep
from django.shortcuts import render
from myinfo import security
from myinfo import client as infoclient
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from uuid import uuid4
import os
import json
from dataclasses import dataclass, fields, asdict
from django.template.defaulttags import register

data_file = "data.json"


@register.filter(name="lookup")
def lookup(value, arg):
    return value.get(arg)


@dataclass
class Person:
    uinfin: str
    name: str
    sex: str
    race: str
    nationality: str
    dob: str
    email: str


field_names = [f.name for f in fields(Person)]


def _parse_person_data(data: dict) -> Person:
    data = {
        k: (data[k]["value"] if "value" in data[k] else data[k]["desc"])
        for k in field_names
    }
    person = Person(**data)
    return person


def _get_decrypted_data(access_token) -> dict:
    client = infoclient.MyInfoClient()
    decoded_access_token = security.get_decoded_access_token(access_token)
    uinfin = decoded_access_token["sub"]
    resp = client.get_person(uinfin=uinfin, access_token=access_token)
    decrypted = security.get_decrypted_person_data(resp)
    return decrypted


def _write_decrypted_data_to_file(data_file, decrypted):
    with open(data_file, "w") as file:
        json.dump(decrypted, file)


# Create your views here.
def singpass_callback(request):
    client = infoclient.MyInfoClient()
    if "code" not in request.GET:
        return HttpResponseBadRequest()
    code = request.GET["code"]
    resp = client.get_access_token(code)
    access_token = resp["access_token"]
    sleep(1)  # sometimes the token is not valid immediately
    decrypted = _get_decrypted_data(access_token)
    _write_decrypted_data_to_file(data_file, decrypted)
    return redirect("/")


def index(request):
    if os.path.exists(data_file):
        data = json.load(open(data_file))
        person = _parse_person_data(data)
        return render(
            request,
            "api/result.html",
            {"person": asdict(person), "field_names": field_names},
        )
    else:
        client = infoclient.MyInfoClient()
        url = client.get_authorise_url(
            state="blahblah", callback_url="http://localhost:3001/callback"
        )
        return render(request, "api/index.html", {"consent_url": url})
