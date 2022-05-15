from django.contrib import admin
from django.contrib.auth.models import Group

# custom
admin.site.unregister(Group)