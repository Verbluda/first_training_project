from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from django.http import HttpResponse
from users.models import Polzovatel, Hospital
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
import json
from marshmallow import ValidationError
from users.schemas import PolzovatelSchema, PolzovatelPatchSchema, PolzovatelSchemaPoints, PolzovatelSchemaPointsGTE, HospitalSchemaCity, HospitalSchemaDoctorCountLTE, HospitalSchema


def request_metrics(func):
    def inner(request):
        print(request.method)
        return func(request)
    return inner


def http_response(text='', status=200):
    response = HttpResponse(text, content_type='application/json')
    response.status_code = status
    return response


@request_metrics
def users(request):
    qs = Polzovatel.objects
    
    if 'points' in request.GET:
        try:
            PolzovatelSchemaPoints().load(request.GET)
            points = int(request.GET['points'])
            qs = qs.filter(points = points)
        except ValidationError as err:
            print(err.messages)
            return http_response(json.dumps(err.messages), 400)

    if 'points_gte' in request.GET:
        try:
            PolzovatelSchemaPointsGTE().load(request.GET)
            points = int(request.GET['points_gte'])
            qs = qs.filter(points__gte = points)
        except ValidationError as err:
            print(err.messages)
            return http_response(json.dumps(err.messages), 400)
            
    users_list = [model_to_dict(user) for user in qs.all()]
    return JsonResponse(users_list, safe = False)
    

@csrf_exempt
@request_metrics
def user(request):
    if request.method == 'GET':
        qs = Polzovatel.objects
        
        if 'id' not in request.GET:
            return http_response('', 400)
        
        try:
            id = int(request.GET['id'])
        except ValueError:
            return http_response('', 400)

        user_obj = qs.filter(id = id).first()

        if not user_obj:
            return http_response('', 404)

        user_obj_dict = model_to_dict(user_obj)
        fav_hospital = model_to_dict(user_obj.fav_hospital)
        user_obj_dict['fav_hospital'] = fav_hospital
        
        return JsonResponse(user_obj_dict, safe = False)
    
    if request.method == 'POST':
        json_body = json.loads(request.body)
        
        try:
            PolzovatelSchema().load(json_body)
        except ValidationError as err:
            print(err.messages)
            return http_response(json.dumps(err.messages), 400)
            
        if Polzovatel.objects.filter(email = json_body['email']).first() is not None:
            return http_response('User email was already created', 400)
           
        if 'fav_hospital' in json_body:
            fav_hospital_obj = Hospital.objects.filter(id = json_body['fav_hospital']).first()
            if fav_hospital_obj is None:
                return http_response('Hospital was not found', 400)
    
            user_obj = Polzovatel(email=json_body['email'], reg_date=json_body['reg_date'], points=json_body['points'], fav_hospital=fav_hospital_obj)
        else:
            user_obj = Polzovatel(email=json_body['email'], reg_date=json_body['reg_date'], points=json_body['points'])

        user_obj.save()
        return JsonResponse(model_to_dict(user_obj), safe = False)
    
    if request.method == 'PATCH':
        json_body = json.loads(request.body)
        
        try:
            PolzovatelPatchSchema().load(json_body)
        except ValidationError as err:
            print(err.messages)
            return http_response(json.dumps(err.messages), 400)
        
        qs = Polzovatel.objects
        
        if 'id' not in request.GET:
            return http_response('', 400)
        
        try:
            id = int(request.GET['id'])
        except ValueError:
            return http_response('', 400)
            
        user_obj = qs.filter(id = id).first()
        
        if user_obj is None:
            return http_response('User was not found', 404)  

        if 'fav_hospital' in json_body:
            hospital_obj = Hospital.objects.filter(id = json_body['fav_hospital']).first()
            if hospital_obj is None:
                return http_response('Hospital was not found', 400)  
            user_obj.fav_hospital = hospital_obj
        
        user_obj.save()
        return JsonResponse(model_to_dict(user_obj), safe = False)
    
    if request.method == 'DELETE':
        if 'id' not in request.GET:
            return http_response('', 400)
            
        try:
            id = int(request.GET['id'])
        except ValueError:
            return http_response('', 400)
           
        user_obj = Polzovatel.objects.filter(id = id).first()
        if user_obj is None:
            return http_response('User was not found', 404)
          
        user_obj.delete()
        return http_response()
       

@csrf_exempt
def hospital(request):
    if request.method == 'GET':
        qs = Hospital.objects
        
        if 'id' not in request.GET:
            return http_response('', 400)
           
        try:
            id = int(request.GET['id'])
        except ValueError:
            return http_response('', 400)
           
        hospital_obj = qs.filter(id = id).first()
        polzovateli_added_as_fav_hospital_objs = hospital_obj.users_added_as_fav.all()
        polzovateli_added_as_fav_hospital = []
        
        for obj in polzovateli_added_as_fav_hospital_objs:
            polzovateli_added_as_fav_hospital.append(model_to_dict(obj))
        
        hospital_dict = model_to_dict(hospital_obj)
        hospital_dict['users_added_as_fav'] = polzovateli_added_as_fav_hospital
        
        if not hospital_obj:
            return http_response('', 404)
        return JsonResponse(hospital_dict, safe = False)
    
    if request.method == 'POST':
        json_body = json.loads(request.body)
        try:
            HospitalSchema().load(json_body)
        except ValidationError as err:
            print(err.message)
            return http_response(json.dumps(err.messages), 400)
            
        if Hospital.objects.filter(name = json_body['name'], city = json_body['city']).first() is not None:
            return http_response('', 400)
           
        hospital_obj = Hospital(name=json_body['name'], city=json_body['city'], adress=json_body['adress'], doctor_count=json_body['doctor_count'])
        hospital_obj.save()
        return JsonResponse(model_to_dict(hospital_obj), safe = False)
    
    if request.method == 'DELETE':
        if 'id' not in request.GET:
            return http_response('', 400)
        
        try:
            id = int(request.GET['id'])
        except ValueError:
            return http_response('', 400)
           
        hospital_obj = Hospital.objects.filter(id = id).first()
        
        if hospital_obj is None:
            return http_response('Hospital was not found)', 404)
            
        if hospital_obj.users_added_as_fav.all():
            return http_response('Sorry', 400)
            
        hospital_obj.delete()
        return http_response() 
        

def hospitals(request):
    qs = Hospital.objects
    
    if 'city' in request.GET:
        try:
            HospitalSchemaCity().load(request.GET)
            city = str(request.GET['city'])
            qs = qs.filter(city = city)
        except ValidationError as err:
            print(err.messages)
            return http_response(json.dumps(err.messages), 400)
           
    if 'doctor_count_lte' in request.GET:
        try:
            HospitalSchemaDoctorCountLTE().load(request.GET)
            doctor_count = int(request.GET['doctor_count_lte'])
            qs = qs.filter(doctor_count__lte = doctor_count)
        except ValidationError as err:
            print(err.messages)
            return http_response(json.dumps(err.messages), 400)
            
    hospitals_list = [model_to_dict(hospital) for hospital in qs.all()]
    return JsonResponse(list(hospitals_list), safe = False)
