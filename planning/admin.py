from django.contrib import admin

from .models import Congress
from .models import Day
from .models import Room
from .models import Session
from .models import Presentation

# Register your models here.

admin.site.register(Day)
admin.site.register(Room)

admin.site.register(Presentation)


class CongressAdmin(admin.ModelAdmin):
    ist_display = ( 'name', 'number')
    readonly_fields = ('id',)
    
admin.site.register(Congress)  

    
class SessionAdmin(admin.ModelAdmin):
    list_display = ( 'room', 'date', 'title', 'order')
    search_fields = ('title',)
    list_filter = ('date',)
    ordering = ('-date',)
    
admin.site.register(Session, SessionAdmin)