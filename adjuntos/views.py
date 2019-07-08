from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from django.db import IntegrityError
from django.views.generic.edit import CreateView, FormView
from django.utils.decorators import method_decorator
from elecciones.views import StaffOnlyMixing
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.functional import cached_property
import base64
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from .models import Attachment, Identificacion
from .forms import IdentificacionForm, AgregarAttachmentsForm


@login_required
def elegir_adjunto(request):
    """
    Elige un acta al azar del queryset :meth:`Attachment.sin asignar`,
    estampa el tiempo de "asignación" para que se excluya durante el periodo
    de guarda y redirige a la vista para la clasificación de la mesa elegida

    Si no hay más mesas sin asignar, se muestra un mensaje estático.
    """

    attachments = Attachment.sin_identificar(0, request.user.fiscal)
    if attachments.exists():
        # TODO: deberiamos priorizar attachments que ya tienen carga
        #       para maximizar la cola de actas cargables
        a = attachments.order_by('?').first()
        # se marca el adjunto
        a.taken = timezone.now()
        a.save(update_fields=['taken'])
        return redirect('asignar-mesa', attachment_id=a.id)

    return render(request, 'adjuntos/sin-actas.html')



class IdentificacionCreateView(CreateView):
    """
    Esta es la vista que permite clasificar un acta,
    asociandola a una mesa o reportando un problema

    Ver :class:`adjuntos.forms.IdentificacionForm`
    """

    form_class = IdentificacionForm
    template_name = "adjuntos/asignar-mesa.html"
    model = Identificacion

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        return response

    def get_success_url(self):
        return reverse('elegir-adjunto')

    @cached_property
    def attachment(self):
        return get_object_or_404(
            Attachment, id=self.kwargs['attachment_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attachment'] = self.attachment
        context['button_tabindex'] = 2
        return context

    def form_valid(self, form):
        identicacion = form.save(commit=False)
        identicacion.fiscal = self.request.user.fiscal
        identicacion.attachment = self.attachment
        return super().form_valid(form)


@staff_member_required
@csrf_exempt
def editar_foto(request, attachment_id):
    """
    esta vista se invoca desde el plugin DarkRoom con el contenido
    de la imágen editada codificada en base64.

    Se decodifica y se guarda en el campo ``foto_edited``
    """
    attachment = get_object_or_404(Attachment, id=attachment_id)
    if request.method == 'POST' and request.POST['data']:
        data = request.POST['data']
        file_format, imgstr = data.split(';base64,')
        extension = file_format.split('/')[-1]
        attachment.foto_edited = ContentFile(base64.b64decode(imgstr), name=f'edited_{attachment_id}.{extension}')
        attachment.save(update_fields=['foto_edited'])
        return JsonResponse({'message': 'Imágen guardada'})
    return JsonResponse({'message': 'No se pudo guardar la imágen'})


class AgregarAdjuntos(FormView):
    """
    Permite subir una o más imágenes, generando instancias de ``Attachment``
    Si una imágen ya existe en el sistema, se exluye con un mensaje de error
    via `messages` framework.

    """

    form_class = AgregarAttachmentsForm
    template_name = 'adjuntos/agregar-adjuntos.html'
    success_url = 'agregada'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            c = 0
            for f in files:
                if f.content_type not in ('image/jpeg', 'image/png'):
                    messages.warning(self.request, f'{f.name} ignorado. No es una imágen' )
                    continue

                try:
                    instance = Attachment(
                        mimetype=f.content_type
                    )
                    instance.foto.save(f.name, f, save=False)
                    instance.save()
                    c += 1
                except IntegrityError:
                    messages.warning(self.request, f'{f.name} ya existe en el sistema' )

            if c:
                messages.success(self.request, f'Subiste {c} imagenes de actas. Gracias!')
            return redirect('agregar-adjuntos')
        else:
            return self.form_invalid(form)
