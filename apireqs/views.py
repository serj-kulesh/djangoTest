from os import path as os_path
from django.template import loader
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
import ssl
from urllib import request as urllib_request


def index(req):
    """ Base api_url could be changed in a template """
    api_url = 'https://slb.medv.ru/api/v2/'
    template = loader.get_template('main_tpl.html')
    context = {'api_url': api_url}

    return HttpResponse(template.render(context))


@csrf_exempt
def send_data(request):
    try:
        cur_d = os_path.dirname(os_path.abspath(__file__))
        key_file = cur_d + '/key_f.key'
        crt_file = cur_d + '/crt_f.crt'
        with open(key_file, 'w') as key_f:
            key_f.write(settings.KEY)
        
        with open(crt_file, 'w') as crt_f:
            crt_f.write(settings.CERT)
    except:
        return JsonResponse({
                'status': 'error',
                'error': 'could\'d not create temp cert files'
            })
    if request.method == "POST":
        if "method" not in request.POST or \
            "api_url" not in request.POST:
            return JsonResponse({
                "status":"error",
                "error": "There is no method or api_url in request object"
            })
        json_to_send = {"jsonrpc": "2.0"}
        url = request.POST["api_url"] if request.POST["api_url"] != "" else ""
        if request.POST["method"] != "":
            method = request.POST["method"]  
        else:
            method = ""
        json_to_send["method"] = method
    
        for i,v in request.POST.items():
            if i == "api_url" or i == "method" or v == "":
                continue

            json_to_send[i] = v
        
        context = ssl.create_default_context()
        context.load_cert_chain(crt_file, key_file)
        j_t_s = json.dumps(json_to_send)
        req = urllib_request.Request('https://slb.medv.ru/api/v2/', 
                                        data=j_t_s.encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        resp = urllib_request.urlopen(req, context=context)
        resp = resp.read().decode('utf-8')
        resp = json.dumps({"response": "None"}) if resp == "None" else resp
    else:
        return JsonResponse({
                "status":"error",
                "error": "Not available method. Please, use POST to send data"
            })
    return JsonResponse({
            'status':'ok',
            'json_request': j_t_s,
            'json_response': str(resp)
        })
