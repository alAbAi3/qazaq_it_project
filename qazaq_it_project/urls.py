# qazaqit_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # 👈 Осы импортты қосыңыз
from django.conf.urls.static import static # 👈 Осы импортты қосыңыз

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# 👇 ФАЙЛДЫҢ СОҢЫНА ОСЫ ЖОЛДЫ ҚОСЫҢЫЗ
# Бұл жол DEBUG режимінде медиа файлдарды көрсетуге мүмкіндік береді
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)