from django.urls import path

from .views import main_page, building_page, node_page, unit_page

urlpatterns = [
    path('', main_page),
    path('building/<int:building_id>/', building_page, name='building_detail'),
    path('node/<int:node_id>/', node_page, name='node_detail'),
    path('unit/<int:unit_id>/', unit_page, name='unit_detail'),
]

