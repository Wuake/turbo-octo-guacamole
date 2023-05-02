import json
#from django.contrib.auth.decorators import user_passes_test
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.db.models import Q
#from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CongressForm, PresentationForm, SessionForm
from .models import *

# * Modification du titre d'une salle
def updateText(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id_salle = data.get("id", "")
        updated_text = data.get("text", "")
        if updated_text == "":
            updated_text = "Salle"
        # Faites ici quelque chose avec le texte mis à jour, comme l'enregistrer en base de données
        print("id_salle : ", id_salle, " updated_text : ", updated_text)
        Room.objects.filter(id=id_salle).update(name=updated_text)
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})

def addOneRoom(new):
    # * Si il y a plusieurs congres,
    # * mettre à jour cette fonction qui va chercher le dernier congres créé
    try:
        # * premier élément du QuerySet retourné 
        new = Congress.objects.all().order_by('-id')[0]
    except Congress.DoesNotExist:
        new = None
    if new :
        rooms = Room.objects.all()
        Room.objects.create(congress= new , number=str(rooms.count()+1), name="Salle "+str(rooms.count()+1))
        status = "salle ajoutée"
    else :
        #retournement d'erreur
        print("erreur lors de la creation de la salle => pas de congres en cours")
        status = "error de creation de la salle => pas de congres en cours"

    return JsonResponse({'status': status})

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

"""
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
"""

def ajax_load_planning(request, pk, date):
    today = date
    presentations = Presentation.objects.select_related('session').filter(session__room_id=pk, session__date=today)
    


    presentations_list = []
    for presentation in presentations:
        interpresents = InterPresent.objects.filter(id_presentation=presentation.pk)
        inter_list = []
        infos = []
        infos_id = []

        #on itere sur les interpresent
        for interp in interpresents:
            # print(interp.id_intervenant)
            # infos_id.append(interp.id_intervenant.id)
            # print(infos_id)
            # print(interp.id_intervenant.id)
            inter_dict = {
                'id': interp.id_intervenant.id,
                'nom': interp.id_intervenant.nom,
                'prenom': interp.id_intervenant.prenom
            }   
            inter_list.append(inter_dict)

        #On met le tout dans un tableau pour afficher les différents noms et prenoms des gens qui ont une présentation
        for personne in inter_list:
            # print(personne)
            infos.append(" " + personne['nom'] + " " + personne['prenom'])
            infos_id.append(personne['id'])
        print(infos_id)

        # print(infos)

        presentation_dict = {
            "id": presentation.pk,
            "title": presentation.title,
            "author": infos,
            "author_id": infos_id,  
            "duration": presentation.duration,
            "session_id": presentation.session_id,
            "session_title": presentation.session.title,
            "time_begin": presentation.session.time_start.strftime('%H:%M'),
            
            "time_end": presentation.session.time_end.strftime('%H:%M'),
        }
        print(presentation.session.time_start.strftime('%H:%M'), presentation.session.time_end.strftime('%H:%M'))
        presentations_list.append(presentation_dict)

    return JsonResponse(presentations_list, safe=False)

# * charge les salles d'un congres
# * prend en param l'id du congres
def ajax_load_rooms(request):
    # retire la ligne là si y'a plusieurs congrès et passe en param le pk du congrès visé
    pk = Congress.objects.all().order_by('-id')[0]
    rooms = Room.objects.filter(congress__pk=pk.id)
    rooms_list = [{
        "id": room.pk,
        "name": room.name,
        "congress": room.congress.name,
        "number": room.number,
    } for room in rooms]
    print("Salut à tous c'est la salle")
    return JsonResponse(rooms_list, safe=False)


#@login_required
def ajax_add_session(request, pk):
    response_data = {}
    today = date.today()
    if request.method == 'POST':
        jsonbody = json.loads(request.body)
        print("_________________________________________________________", jsonbody['id'],  jsonbody['title'])
        try:
            new = Session.objects.get(id=int(jsonbody['id']))
        except Session.DoesNotExist:
            new = None

        if new is None:
            start_time = datetime.strptime(jsonbody['time1'], '%H:%M').time()
            end_time = datetime.strptime(jsonbody['time2'], '%H:%M').time()
            date_id = jsonbody['date']
            existing_sessions = Session.objects.filter(
                Q(room_id=pk) & Q(date_id=date_id) &
                (Q(time_start__lt=end_time) & Q(time_end__gt=start_time))
            )
            if existing_sessions.exists():
                response_data['error'] = 'Une session existe déjà à ce moment-là'
            else:
                sess = Session.objects.create(
                    room_id=pk,
                    date_id=date_id,
                    title=jsonbody['title'],
                    time_start=start_time,
                    time_end=end_time
                )
                if sess:
                    Presentation.objects.create(
                        session_id=sess.id,
                        title='Présentation',
                        duration=30,
                    )
                response_data['success'] = 'Session créée avec succès'
        else:
            start_time = datetime.strptime(jsonbody['time1'], '%H:%M').time()
            end_time = datetime.strptime(jsonbody['time2'], '%H:%M').time()
            date_id = jsonbody['date']
            existing_sessions = Session.objects.filter(
                Q(room_id=pk) & Q(date_id=date_id) & ~Q(id=new.id) &
                (Q(time_start__lt=end_time) & Q(time_end__gt=start_time))
            )
            if existing_sessions.exists():
                response_data['error'] = 'Une session existe déjà à ce moment-là'
            else:
                new.title = jsonbody['title']
                new.time_start = start_time
                new.time_end = end_time
                new.save()
                response_data['success'] = 'Session mise à jour avec succès'

    presentations_list = {}
    return JsonResponse(response_data, safe=False)

#@login_required
def ajax_add_pres(request, pk):
    #posts = Post.objects.all()
    response_data = {}
    today = date.today()
    if request.method == 'POST':
        jsonbody = json.loads(request.body)

        response_data['title'] = jsonbody['title']
        response_data['time2'] = jsonbody['duration']
        response_data['author'] = jsonbody['author']
        response_data['author1'] = jsonbody['author1']
        response_data['author2'] = jsonbody['author2']

        # ! REGLER LE BUG DE MODIFICATION DES INFORMATIONS DE PRESENTATION

        try:
            new = Presentation.objects.get(id=int(jsonbody['id']))
            
        except Presentation.DoesNotExist:
            new = None           
            
        if new :
            
            new.session_id = pk
            new.title=jsonbody['title']
            
            # new.author=jsonbody['author']
            new.duration=jsonbody['duration']
            InterPresent.objects.filter(id_presentation=new).delete()
            new.save()
        else :
        
            new =  Presentation.objects.create( session_id = pk,
                                                title = jsonbody['title'],
                                                # author= jsonbody['author'],
                                                duration= jsonbody['duration'],
                                                )
        

        try:
            new_inter = InterPresent.objects.get(id=int(jsonbody['id']))
            new_intervenant = Intervenant.objects.get(id=int(jsonbody['author']))
            new_intervenant1 = Intervenant.objects.get(id=int(jsonbody['author1']))
            new_intervenant2 = Intervenant.objects.get(id=int(jsonbody['author2']))
            
        except InterPresent.DoesNotExist:
            new_inter = None
            new_intervenant = Intervenant.objects.get(id=int(jsonbody['author']))
            if(jsonbody['author1']):
                new_intervenant1 = Intervenant.objects.get(id=int(jsonbody['author1']))
                
                if(jsonbody['author2']):
                    new_intervenant2 = Intervenant.objects.get(id=int(jsonbody['author2']))


        if new_inter :
            new_inter.id_presentation = new
            new_inter.id_intervenant=new_intervenant
            if(jsonbody['author1']):
                new_inter.id_intervenant=new_intervenant1
                if(jsonbody['author2']):
                    new_inter.id_intervenant=new_intervenant2
            new_inter.save()
        else :
            existing_inter = InterPresent.objects.filter(id_presentation=new, id_intervenant=new_intervenant)
            if(jsonbody['author1']):
                existing_inter1 = InterPresent.objects.filter(id_presentation=new, id_intervenant=new_intervenant1)
            else:
                existing_inter1 = None
            if(jsonbody['author2']):
                existing_inter2 = InterPresent.objects.filter(id_presentation=new, id_intervenant=new_intervenant2)
            else:
                existing_inter2 = None

            if not existing_inter:
               
               new_inter = InterPresent.objects.create( id_presentation = new,
                                                     id_intervenant = new_intervenant,
                                                     )
            else:
                existing_inter.first().delete()
                new_inter = InterPresent.objects.create( id_presentation = new,
                                                     id_intervenant = new_intervenant,
                                                     )

            if not existing_inter1:
                if(jsonbody['author1']):
                    new_inter = InterPresent.objects.create( id_presentation = new,
                                                            id_intervenant = new_intervenant1,
                                                            )
            if not existing_inter2:
                if(jsonbody['author2']):
                    new_inter = InterPresent.objects.create( id_presentation = new,
                                                            id_intervenant = new_intervenant2,
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
    