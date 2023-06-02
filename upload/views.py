from django.shortcuts import render
from django.http import JsonResponse
import os
from planning.models import Intervenant, File, Presentation

def uploadfile(request):
    intervenant_all = Intervenant.objects.all()
    if request.method == 'POST':  
        file = request.FILES['file'].read()
        fileName= request.POST['filename']
        existingPath = request.POST['path']
        end = request.POST['end']
        nextSlice = request.POST['nextSlice']
        aborted = request.POST['aborted']
        id_presta = request.POST['id_presta']
        
        print("_________aborted____________", aborted)
        if file=="" or fileName=="" or existingPath=="" or end=="" or nextSlice=="" :
            res = JsonResponse({'data':'Invalid Request....'})
            return res
        else:
            if existingPath == 'null':
                path = 'media/presentations/' + fileName
                with open(path, 'wb+') as destination: 
                    destination.write(file)
                FileFolder = File()
                FileFolder.existingPath = path
                FileFolder.path = path
                FileFolder.eof = end
                FileFolder.name = fileName
                FileFolder.save()

                #lien entre le fichier upload et la présentation
                if id_presta != 'null':
                    print("_________id_presta____________", id_presta)
                    presta = Presentation.objects.get(id=id_presta)
                    print("_________presta____________", presta)
                    presta.fichier_pptx = FileFolder
                    print("_________presta_fichier____________", presta.fichier_pptx)
                    presta.save()

                if int(end):
                    res = JsonResponse({'data':'Uploaded Successfully...','existingPath': fileName})
                else:
                    res = JsonResponse({'existingPath': fileName})
                return res

            else:
                path = 'media/presentations/' + existingPath
                #print("_________aborted____________", path, existingPath)
                model_id = File.objects.get(existingPath=path)
                
                if  model_id.name == fileName and  aborted=='1': 
                    print("_________DELETED___________",  existingPath)
                    model_id.delete()
                    os.remove(path)
                    res = JsonResponse({'data':'Upload Aborted!!', 'existingPath':'Aborted'})
                    return res
                elif model_id.name == fileName:
                    if not model_id.eof:
                        with open(path, 'ab+') as destination: 
                            destination.write(file)
                        if int(end):
                            model_id.eof = int(end)
                            model_id.save()
                            res = JsonResponse({'data':'Uploaded Successfully','existingPath':model_id.existingPath})
                        else:
                            res = JsonResponse({'existingPath':model_id.name})    
                        return res
                    else:
                        res = JsonResponse({'data':'EOF found. Invalid request'})
                        return res
                else:
                    res = JsonResponse({'data':'No such file exists in the existingPath'})
                    return res
    return render(request, 'Planning/upload.html', {'intervenant_all':intervenant_all})