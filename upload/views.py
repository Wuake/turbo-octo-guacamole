from django.shortcuts import render
from django.http import JsonResponse
import os
from .models import File
from planning.models import Intervenant

def uploadfile(request):
    intervenant_all = Intervenant.objects.all()
    if request.method == 'POST':  
        file = request.FILES['file'].read()
        fileName= request.POST['filename']
        existingPath = request.POST['existingPath']
        end = request.POST['end']
        nextSlice = request.POST['nextSlice']
        aborted = request.POST['aborted']
        
        print("_________aborted____________", aborted)
        if file=="" or fileName=="" or existingPath=="" or end=="" or nextSlice=="" :
            res = JsonResponse({'data':'Invalid Request....'})
            return res
        else:
            if existingPath == 'null':
                path = 'media/' + fileName
                with open(path, 'wb+') as destination: 
                    destination.write(file)
                FileFolder = File()
                FileFolder.existingPath = path
                FileFolder.eof = end
                FileFolder.name = fileName
                FileFolder.save()
                if int(end):
                    res = JsonResponse({'data':'Uploaded Successfully...','existingPath': fileName})
                else:
                    res = JsonResponse({'existingPath': fileName})
                                       
                return res

            else:
                path = 'media/' + existingPath
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