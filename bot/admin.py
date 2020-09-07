from django.contrib import admin
from .models import Imageupload

#admin.site.register(Imageupload)
@admin.register(Imageupload)
class ImageuploadAdmin(admin.ModelAdmin):
    list_display = ('date_of_upload', 'title', 'image_file')
