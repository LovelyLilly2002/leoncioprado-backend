# apps/usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cuenta, PerfilUsuario, Turno, Nivel, Grado


# --- 1. ADMIN PERSONALIZADO PARA Cuenta y PerfilUsuario ---

# Inline para ver y editar el PerfilUsuario desde la Cuenta
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False  # Previene la eliminación accidental del perfil
    verbose_name_plural = 'Información Adicional del Perfil'
    fieldsets = (
        (None, {
            'fields': ('dni', 'nombre', 'apellido', 'telefono', 'grado')
        }),
    )

# Admin personalizado para Cuenta (Hereda de UserAdmin)
@admin.register(Cuenta)
class CuentaAdmin(UserAdmin):
    # Campos a mostrar en la lista
    list_display = ('username', 'email', 'get_full_name', 'rol', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'dni') # DNI lo añadimos a la búsqueda
    ordering = ('username',)

    # Secciones del formulario de edición de la cuenta
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos y Roles', {'fields': ('is_active', 'is_staff', 'is_superuser', 'rol', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    # Añadir el PerfilUsuario como un campo en línea
    inlines = [PerfilUsuarioInline]
    
    # Aseguramos que el campo 'rol' se muestre al crear o editar
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('rol', 'email', 'first_name', 'last_name')}),
    )
    
    # Sobrescribir get_fieldsets para incluir 'rol' en el formulario de edición
    def get_fieldsets(self, request, obj=None):
        if obj: # Edición
            return self.fieldsets
        return self.add_fieldsets

# Registramos el PerfilUsuario, aunque se puede acceder desde Cuenta,
# es útil para búsquedas directas.
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombre', 'apellido', 'cuenta', 'grado')
    search_fields = ('dni', 'nombre', 'apellido', 'cuenta__username')
    list_filter = ('grado__nivel', 'grado__turno')


# --- 2. ADMIN PARA MODELOS DE CATÁLOGO ---

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    # Muestra todos los campos clave en la lista
    list_display = ('nombre', 'seccion', 'nivel', 'turno', 'count_usuarios')
    search_fields = ('nombre', 'seccion', 'nivel__nombre', 'turno__nombre')
    list_filter = ('nivel', 'turno')
    ordering = ('nivel__nombre', 'nombre', 'seccion')
    
    # Campo personalizado para mostrar cuántos usuarios están asignados a este grado
    def count_usuarios(self, obj):
        # Contamos cuántos PerfilUsuario tienen este Grado
        return obj.perfilusuario_set.count() 

    count_usuarios.short_description = "N° Usuarios"