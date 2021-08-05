from django.contrib import admin

from .models import Building, Node, Unit

admin.site.site_title = ''
admin.site.site_header = 'Администрирование диспетчеризации'


class NodeInlines(admin.StackedInline):
    model = Node
    extra = 0


class UnitInlines(admin.StackedInline):
    model = Unit
    extra = 0


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    inlines = (NodeInlines,)

    class Meta:
        model = Building


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'building', 'name')
    list_display_links = ('name',)
    list_filter = ('building',)
    inlines = (UnitInlines,)

    class Meta:
        model = Node


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('node', 'name')
    list_display_links = ('name',)
    list_filter = ('node',)

    class Meta:
        model = Unit
