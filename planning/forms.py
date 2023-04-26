from planning.models import Congress, InterPresent, Intervenant
from django import forms

       
class CongressForm(forms.Form):
    id = forms.CharField(label='', initial=-1,widget=forms.TextInput(attrs={'type': 'hidden', 'id':"cong_id"}) )
    label = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'label', 'id':"cong_label"}) )
    description = forms.CharField(label='', widget=forms.Textarea( attrs={"rows":"4", 'placeholder': 'Description..', 'id':"vid_body"} ))
    thumbnail = forms.ImageField(label='', widget=forms.FileInput(attrs={'placeholder': 'Vignette de la vidéo', 'id':"vid_thumb"}) )
    number = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Nombre de salles', 'id':"cong_number"}) )  
    date1 = forms.CharField(label='',widget=forms.DateInput(attrs={'type': 'date','placeholder': 'Date de début', 'id':"date1"}) ) 
    date2 = forms.CharField(label='',widget=forms.DateInput(attrs={'type': 'date','placeholder': 'Date de fin', 'id':"date2"}) ) 
    
class SessionForm(forms.Form):
    id = forms.CharField(label='', initial=-1,widget=forms.TextInput(attrs={'type': 'hidden', 'id':"sess_id"}) )
    name = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Nom de session', 'id':"sess_name"}) )
    date1 = forms.CharField(label='',widget=forms.TimeInput(attrs={'type': 'time','format':'%H:%M','placeholder': 'Heure de début', 'id':"sess_time1"}) ) 
    date2 = forms.CharField(label='',widget=forms.TimeInput(attrs={'type': 'time','format':'%H:%M','placeholder': 'Heure de fin', 'id':"sess_time2"}) ) 

class PresentationForm(forms.Form):
    id = forms.CharField(label='', initial=-1,widget=forms.TextInput(attrs={'type': 'hidden', 'id':"pres_id"}) )
    name = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Titre de la présentation', 'id':"pres_name"}) )
    
    author = forms.ModelChoiceField(queryset=Intervenant.objects.all(), label='',widget=forms.Select(attrs={'placeholder': 'Auteurs', 'id':"pres_author"}) )
    duration = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Durée de la présentation', 'id':"pres_duration"}) )