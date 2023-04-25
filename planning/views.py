from django.shortcuts import render, get_object_or_404, redirect
#from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http.response import JsonResponse
from django.contrib import messages
#from django.contrib.auth.decorators import user_passes_test
from datetime import date, timedelta, datetime
import json
# Create your views here.

from .models import *
from .forms import CongressForm, SessionForm, PresentationForm

def addRooms(new, nb):
    i=1
    while i <= int(nb) :
        Room.objects.create(congress= new , number=str(i), name="Salle "+str(i))
        i = i+1
        
def addDay(new,date1, date2):
    delta = timedelta(days=1)
    while date1 <= date2:
        #print(date1, date1.strftime("%Y-%m-%d"))
        Day.objects.create(congress= new,date=date1) 
        date1 += delta       
        
    
#selection de la presentation en cours pour affichage dans le live
#@user_passes_test(lambda u: u.is_superuser)
def addcongres(request):
    if request.method == "POST":
        add_form = CongressForm(request.POST,request.FILES)
        if add_form.is_valid():
            id = add_form.cleaned_data['id']
            label = add_form.cleaned_data['label']
            number = add_form.cleaned_data['number']
            description = add_form.cleaned_data['description']
            thumbnail = add_form.cleaned_data['thumbnail']
            date1 = add_form.cleaned_data['date1']
            date2 = add_form.cleaned_data['date2']
            try:
                new = Congress.objects.get(id=id)
            except Congress.DoesNotExist:
                new = None           
            #new, created = Video.objects.get_or_create(id=id, defaults={'title':title, 'name':name, 'body':body, 'thumbnail':thumbnail } )
            if new :
                new.name=label
                new.description=description
                new.thumbnail=thumbnail
            else :
                new = Congress.objects.create(name=label, number=number, description=description, thumbnail=thumbnail)
                
            new.save()
            addRooms(new, number)
            addDay(new, datetime.strptime(date1, '%Y-%m-%d').date(), datetime.strptime(date2, '%Y-%m-%d').date() )
            messages.success(request,'Un nouveau congrès a été crée : '+ add_form['label'].value())
        else : messages.error(request,'Formulaire invalide : '+add_form.errors)
       
    form = CongressForm()
    return render(request, "Planning/congres.html", {"add_form":form}) 

# mise a jour de la presentation en cours dans le champ dedié de la room pour affichage dans le live
#@user_passes_test(lambda u: u.is_superuser)
def create(request):
    congres = Congress.objects.get()
    rooms = Room.objects.filter(congress__pk=congres.pk)
    days = Day.objects.filter(congress__pk=congres.pk)
    pform = PresentationForm()
    sform = SessionForm()
    return render(request, "Planning/create.html", {'rooms': rooms,'days': days,"sess_form":sform, "pres_form":pform}) 


def show_plan(request):
    congres = Congress.objects.get()
    rooms = Room.objects.filter(congress__pk=congres.pk)
    return render(request, 'Planning/show.html', {'rooms': rooms})


#@login_required
def ajax_load_planning(request, pk, date):
    today = date
    #today = '2023-04-18'
    presentations = Presentation.objects.select_related('session').filter(session__room_id=pk, session__date=today)
	
	#print(presentations.query)
    presentations_list = [{
        "id": presentation.pk,
        "title": presentation.title,
        "author": presentation.author,
        "duration": presentation.duration,
        "session_id": presentation.session_id,
        "session_title": presentation.session.title,
        "time_begin": presentation.session.time_start,
        "time_end": presentation.session.time_end,

    } for presentation in presentations ]
    
    return JsonResponse(presentations_list, safe=False)

#@login_required
def ajax_add_session(request, pk):
    #posts = Post.objects.all()
    response_data = {}
    today = date.today()
    if request.method == 'POST':
        jsonbody = json.loads(request.body)
        print("_________________________________________________________", jsonbody['id'],  jsonbody['title'])
        try:
            new = Session.objects.get(id=int(jsonbody['id']))
        except Session.DoesNotExist:
            new = None  
        
        if new :
            new.title=jsonbody['title']
            new.time_start=jsonbody['time1']
            new.time_end=jsonbody['time2']
            new.save()
        else :
            sess = Session.objects.create( room_id = pk,
                                            date_id = jsonbody['date'],
                                            title = jsonbody['title'],
                                            time_start= jsonbody['time1'],
                                            time_end= jsonbody['time2'],
                                            )
            if sess :
                Presentation.objects.create(
                session_id = sess.id,
                title = 'Présentation',
                author= 'autheur',
                duration= 30,
                )
    presentations_list = { }
    return JsonResponse(presentations_list, safe=False)

#@login_required
def ajax_add_pres(request, pk):
    #posts = Post.objects.all()
    response_data = {}
    today = date.today()
    if request.method == 'POST':
        jsonbody = json.loads(request.body)

        response_data['title'] = jsonbody['title']
        response_data['time1'] = jsonbody['author']
        response_data['time2'] = jsonbody['duration']

        try:
            new = Presentation.objects.get(id=int(jsonbody['id']))
        except Presentation.DoesNotExist:
            new = None           
            
        if new :
            new.session_id = pk
            new.title=jsonbody['title']
            new.author=jsonbody['author']
            new.duration=jsonbody['duration']
            new.save()
        else :
            new =  Presentation.objects.create( session_id = pk,
                                                title = jsonbody['title'],
                                                author= jsonbody['author'],
                                                duration= jsonbody['duration'],
                                                )
            
    return JsonResponse(response_data, safe=False)

#@user_passes_test(lambda u: u.is_superuser)
def ajax_del_pres(request, pk):
    if request.method == 'POST':
        jsonbody = json.loads(request.body)
        
        if jsonbody['is_sess'] == 1 :
            Session.objects.filter(id=pk).delete()
        else : 
            Presentation.objects.filter(id=pk).delete()
    
    return JsonResponse({}, safe=False)    
    