from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from registrostxtss.models import RegistrosTxTss, RSitio, RAcceso, REmpalme
from registrostxtss.services.pdf_report_service import PDFReportService


@login_required
def reports_dashboard(request):
    """
    Dashboard principal para los informes
    """
    # Estadísticas generales
    total_registros = RegistrosTxTss.objects.filter(is_deleted=False).count()
    registros_con_sitio = RegistrosTxTss.objects.filter(
        rsitio__isnull=False, 
        rsitio__is_deleted=False
    ).distinct().count()
    registros_con_acceso = RegistrosTxTss.objects.filter(
        racceso__isnull=False, 
        racceso__is_deleted=False
    ).distinct().count()
    registros_con_empalme = RegistrosTxTss.objects.filter(
        rempalme__isnull=False, 
        rempalme__is_deleted=False
    ).distinct().count()
    
    # Porcentajes de completitud
    porcentaje_sitio = (registros_con_sitio / total_registros * 100) if total_registros > 0 else 0
    porcentaje_acceso = (registros_con_acceso / total_registros * 100) if total_registros > 0 else 0
    porcentaje_empalme = (registros_con_empalme / total_registros * 100) if total_registros > 0 else 0
    
    context = {
        'total_registros': total_registros,
        'registros_con_sitio': registros_con_sitio,
        'registros_con_acceso': registros_con_acceso,
        'registros_con_empalme': registros_con_empalme,
        'porcentaje_sitio': round(porcentaje_sitio, 1),
        'porcentaje_acceso': round(porcentaje_acceso, 1),
        'porcentaje_empalme': round(porcentaje_empalme, 1),
    }
    
    return render(request, 'registrostxtss/reports/dashboard.html', context)


@login_required
def generate_complete_pdf_report(request):
    """
    Genera un informe completo en PDF de todos los registros
    """
    try:
        pdf_service = PDFReportService()
        
        # Aplicar filtros si se proporcionan
        registros = RegistrosTxTss.objects.filter(is_deleted=False)
        
        # Filtro por sitio
        sitio_id = request.GET.get('sitio_id')
        if sitio_id:
            registros = registros.filter(sitio_id=sitio_id)
        
        # Filtro por usuario
        user_id = request.GET.get('user_id')
        if user_id:
            registros = registros.filter(user_id=user_id)
        
        # Filtro por fecha
        fecha_inicio = request.GET.get('fecha_inicio')
        if fecha_inicio:
            registros = registros.filter(created_at__date__gte=fecha_inicio)
        
        fecha_fin = request.GET.get('fecha_fin')
        if fecha_fin:
            registros = registros.filter(created_at__date__lte=fecha_fin)
        
        # Filtro por completitud
        completitud = request.GET.get('completitud')
        if completitud == 'completo':
            registros = registros.filter(
                rsitio__isnull=False,
                racceso__isnull=False,
                rempalme__isnull=False
            ).distinct()
        elif completitud == 'incompleto':
            registros = registros.filter(
                Q(rsitio__isnull=True) |
                Q(racceso__isnull=True) |
                Q(rempalme__isnull=True)
            ).distinct()
        
        response = pdf_service.generate_complete_report(registros)
        return response
        
    except Exception as e:
        return JsonResponse({
            'error': True,
            'message': f'Error al generar el informe: {str(e)}'
        }, status=500)


@login_required
def generate_summary_pdf_report(request):
    """
    Genera un informe resumido en PDF con estadísticas
    """
    try:
        pdf_service = PDFReportService()
        response = pdf_service.generate_summary_report()
        return response
        
    except Exception as e:
        return JsonResponse({
            'error': True,
            'message': f'Error al generar el informe resumido: {str(e)}'
        }, status=500)


@login_required
def reports_list(request):
    """
    Lista de registros con opciones de filtrado para generar informes
    """
    registros = RegistrosTxTss.objects.filter(is_deleted=False).select_related(
        'sitio', 'user'
    ).prefetch_related(
        'rsitio_set',
        'racceso_set',
        'rempalme_set'
    )
    
    # Filtros
    sitio_id = request.GET.get('sitio_id')
    if sitio_id:
        registros = registros.filter(sitio_id=sitio_id)
    
    user_id = request.GET.get('user_id')
    if user_id:
        registros = registros.filter(user_id=user_id)
    
    fecha_inicio = request.GET.get('fecha_inicio')
    if fecha_inicio:
        registros = registros.filter(created_at__date__gte=fecha_inicio)
    
    fecha_fin = request.GET.get('fecha_fin')
    if fecha_fin:
        registros = registros.filter(created_at__date__lte=fecha_fin)
    
    completitud = request.GET.get('completitud')
    if completitud == 'completo':
        registros = registros.filter(
            rsitio__isnull=False,
            racceso__isnull=False,
            rempalme__isnull=False
        ).distinct()
    elif completitud == 'incompleto':
        registros = registros.filter(
            Q(rsitio__isnull=True) |
            Q(racceso__isnull=True) |
            Q(rempalme__isnull=True)
        ).distinct()
    
    # Paginación
    paginator = Paginator(registros, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener sitios y usuarios para los filtros
    from core.models.sites import Site
    from users.models import User
    
    sitios = Site.objects.all()
    usuarios = User.objects.all()
    
    context = {
        'page_obj': page_obj,
        'sitios': sitios,
        'usuarios': usuarios,
        'filtros_activos': {
            'sitio_id': sitio_id,
            'user_id': user_id,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'completitud': completitud,
        }
    }
    
    return render(request, 'registrostxtss/reports/list.html', context)


@login_required
@require_http_methods(["POST"])
def generate_custom_report(request):
    """
    Genera un informe personalizado basado en los filtros seleccionados
    """
    try:
        # Obtener filtros del formulario
        sitio_ids = request.POST.getlist('sitio_ids')
        user_ids = request.POST.getlist('user_ids')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        completitud = request.POST.get('completitud')
        tipo_reporte = request.POST.get('tipo_reporte', 'completo')
        
        # Construir el queryset base
        registros = RegistrosTxTss.objects.filter(is_deleted=False)
        
        # Aplicar filtros
        if sitio_ids:
            registros = registros.filter(sitio_id__in=sitio_ids)
        
        if user_ids:
            registros = registros.filter(user_id__in=user_ids)
        
        if fecha_inicio:
            registros = registros.filter(created_at__date__gte=fecha_inicio)
        
        if fecha_fin:
            registros = registros.filter(created_at__date__lte=fecha_fin)
        
        if completitud == 'completo':
            registros = registros.filter(
                rsitio__isnull=False,
                racceso__isnull=False,
                rempalme__isnull=False
            ).distinct()
        elif completitud == 'incompleto':
            registros = registros.filter(
                Q(rsitio__isnull=True) |
                Q(racceso__isnull=True) |
                Q(rempalme__isnull=True)
            ).distinct()
        
        # Generar el reporte según el tipo
        pdf_service = PDFReportService()
        
        if tipo_reporte == 'resumen':
            response = pdf_service.generate_summary_report()
        else:
            response = pdf_service.generate_complete_report(registros)
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'error': True,
            'message': f'Error al generar el informe personalizado: {str(e)}'
        }, status=500) 