from django.shortcuts import render, get_object_or_404, redirect
#from django.contrib.auth.decorators import login_required
from django.http import Http404

import socket, base64, json, ftplib as ftp
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.http.response import JsonResponse
from django.contrib import messages
#from django.contrib.auth.decorators import user_passes_test
from datetime import date, timedelta, datetime
from django.core.files.base import ContentFile
from .models import *
from .forms import CongressForm, SessionForm, PresentationForm, IntervenantForm, EditIntervenantForm

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
    congress = Congress.objects.first()
    days = congress.confs_days.all()
    rooms = congress.event_conf_name.all()
    schedule = []

    for day in days:
        day_schedule = {'day': day, 'rooms': []}
        for room in rooms:
            sessions = Session.objects.filter(date=day, room=room).order_by('time_start')
            room_data = {'room': room, 'sessions': []}
            for session in sessions:
                presentations = Presentation.objects.filter(session=session)
                session_data = {'session': session, 'presentations': presentations}
                room_data['sessions'].append(session_data)
            day_schedule['rooms'].append(room_data)
        schedule.append(day_schedule)

    context = {'congress': congress, 'schedule': schedule}
    return render(request, 'Planning/show.html', context)

def show_pupitre(request):
    congres = Congress.objects.get()
    rooms = Room.objects.filter(congress__pk=congres.pk)
    days = Day.objects.filter(congress__pk=congres.pk)
    pform = PresentationForm()
    sform = SessionForm()
    return render(request, "Planning/pupitre.html", {'rooms': rooms,'days': days,"sess_form":sform, "pres_form":pform}) 

def show_intervenant(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if 'id' in request.POST:  # Modification de l'intervenant existant
            intervenant = get_object_or_404(Intervenant, id=request.POST['id'])
            form = EditIntervenantForm(request.POST, request.FILES, instance=intervenant)
        else:  # Création d'un nouvel intervenant
            form = IntervenantForm(request.POST, request.FILES)

        if form.is_valid():
            intervenant = form.save()
            response = {'success': True, 'intervenant': intervenant.to_json()}
        else:
            response = {'success': False, 'errors': form.errors}
        return JsonResponse(response)
    else:
        intervenants = Intervenant.objects.all()
        Intervenant_form = IntervenantForm()
        EditIntervenant_form = EditIntervenantForm()

        context = {
            'intervenants': intervenants,
            'Intervenant_form': Intervenant_form,
            'EditIntervenant_form': EditIntervenant_form,
        }

        return render(request, 'Planning/intervenant.html', context)    

def delete_intervenant(request, intervenant_id):
    try:
        intervenant = Intervenant.objects.get(id=intervenant_id)
        intervenant.delete()
        return JsonResponse({'success': True})
    except Intervenant.DoesNotExist:
        return JsonResponse({'success': False, 'errors': 'Intervenant does not exist.'})


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

def ajax_add_intervenant(request, pk):
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

        print(request.body)

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
            # new.fichier = jsonbody['fichier']
            InterPresent.objects.filter(id_presentation=new).delete()
            new.save()
        else :
            # print(jsonbody["fichier"])
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

def open_ppt(host, ppt_file):
    host = host
    port = 5000
    message = f"open_ppt@{ppt_file}".encode()
    # create socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # connect to server
        sock.connect((host, port))
        # send string to server
        sock.sendall(message)
        # get server response
        response = sock.recv(1024)
        # decode the response and return it
        return response.decode()

def ouvrir_presentation(request):

    data = json.loads(request.body)
    id_pres = data.get('id', '')
    print(id_pres)

    presentation = Presentation.objects.get(id=id_pres)
    print(presentation)
    fichier_pptx = presentation.fichier_pptx
    print("le fichier => " + fichier_pptx.name)
    print("Voici le lien vers le fichier => " + fichier_pptx.path)

    # open_ppt("127.0.0.1", fichier_pptx.path)

    #try catch en python
    try:
        open_ppt("127.0.0.1", fichier_pptx.path)
        res = True
    except:
        print("erreur de connexion au serveur python")
        res = False

    return JsonResponse({"success": res})

def show_upload(request):
    intervenant_all = Intervenant.objects.all()
    print("ok")
    return render(request, 'Planning/upload.html', {'intervenant_all': intervenant_all})

def intervenant_select(request):

    data = json.loads(request.body)
    id = data.get('id', '')

    print(id)
    presentations = Presentation.objects.filter(interpresent__id_intervenant=id)
    presentation_list = []

    for presentation in presentations:
        presentation_list.append({
            'id': presentation.id,
            'title': presentation.title,
            'duration': presentation.duration,
            'fichier_pptx': presentation.fichier_pptx.path if presentation.fichier_pptx else None
        })
    
    return JsonResponse({"presentations": presentation_list})

def upload_file(request):
    file = request.FILES.get("file")
    # fss = FileSystemStorage()
    # filename = fss.save(file.name, file)
    # url = fss.url(filename)
    print(file)
    data = ContentFile(base64.b64decode(file), name=file.name) 
    Presentation.objects.create(doc=data)
    print(data)
    return JsonResponse({"link": data})

def check_mark(request):
    data = json.loads(request.body)
    id = data.get('id', '')
    presentation = Presentation.objects.get(id=id)
    print("VOICI L'ID DE LA PRESENTATION",presentation.id)

    if presentation.fichier_pptx is not None and presentation.fichier_pptx.path is not None:
        res = True
    else:
        res = False
        print("PAS DE PRESENTATION TROUVEE DANS LA BASE DE DONNEES")

    return JsonResponse({"success": res})
