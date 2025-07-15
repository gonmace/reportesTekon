import os
from datetime import datetime
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from registrostxtss.models import RegistrosTxTss, RSitio, RAcceso, REmpalme


class PDFReportService:
    """
    Servicio para generar informes en PDF de registros Tx/Tss
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el reporte"""
        # Estilo para títulos principales
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.darkblue
        ))
        
        # Estilo para encabezados de tabla
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER
        ))
        
        # Estilo para datos de tabla
        self.styles.add(ParagraphStyle(
            name='TableData',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT
        ))
    
    def generate_complete_report(self, registros=None):
        """
        Genera un informe completo de todos los registros Tx/Tss
        
        Args:
            registros: QuerySet de registros (opcional, si no se proporciona usa todos)
            
        Returns:
            HttpResponse con el PDF generado
        """
        if registros is None:
            registros = RegistrosTxTss.objects.filter(is_deleted=False).select_related(
                'sitio', 'user'
            ).prefetch_related(
                'rsitio_set',
                'racceso_set', 
                'rempalme_set'
            )
        
        # Crear el buffer para el PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                               topMargin=72, bottomMargin=72)
        
        # Lista de elementos del PDF
        story = []
        
        # Título principal
        story.append(Paragraph("INFORME COMPLETO DE REGISTROS TX/TSS", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Información del reporte
        story.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                              self.styles['Normal']))
        story.append(Paragraph(f"Total de registros: {registros.count()}", self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Generar contenido para cada registro
        for registro in registros:
            story.extend(self._generate_registro_section(registro))
            story.append(PageBreak())
        
        # Construir el PDF
        doc.build(story)
        
        # Obtener el valor del buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Crear la respuesta HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="informe_registros_txtss_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        response.write(pdf)
        
        return response
    
    def _generate_registro_section(self, registro):
        """Genera la sección de un registro específico"""
        elements = []
        
        # Título del registro
        elements.append(Paragraph(f"REGISTRO: {registro.sitio} - {registro.user}", 
                                 self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 15))
        
        # Información básica del registro
        basic_info = [
            ['Campo', 'Valor'],
            ['Sitio', str(registro.sitio)],
            ['Usuario', str(registro.user)],
            ['Fecha de creación', registro.created_at.strftime('%d/%m/%Y %H:%M')],
            ['Estado', 'Activo' if not registro.is_deleted else 'Eliminado']
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(basic_table)
        elements.append(Spacer(1, 20))
        
        # Sección de Sitio
        rsitio = registro.rsitio_set.filter(is_deleted=False).first()
        if rsitio:
            elements.extend(self._generate_sitio_section(rsitio))
        
        # Sección de Acceso
        racceso = registro.racceso_set.filter(is_deleted=False).first()
        if racceso:
            elements.extend(self._generate_acceso_section(racceso))
        
        # Sección de Empalme
        rempalme = registro.rempalme_set.filter(is_deleted=False).first()
        if rempalme:
            elements.extend(self._generate_empalme_section(rempalme))
        
        return elements
    
    def _generate_sitio_section(self, rsitio):
        """Genera la sección de información del sitio"""
        elements = []
        
        elements.append(Paragraph("INFORMACIÓN DEL SITIO", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 10))
        
        sitio_data = [
            ['Campo', 'Valor'],
            ['Latitud', str(rsitio.lat)],
            ['Longitud', str(rsitio.lon)],
            ['Altura Torre', rsitio.altura],
            ['Dimensiones', rsitio.dimensiones],
            ['Deslindes', rsitio.deslindes],
            ['Comentarios', rsitio.comentarios or 'Sin comentarios']
        ]
        
        sitio_table = Table(sitio_data, colWidths=[2*inch, 4*inch])
        sitio_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(sitio_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _generate_acceso_section(self, racceso):
        """Genera la sección de información de acceso"""
        elements = []
        
        elements.append(Paragraph("INFORMACIÓN DE ACCESO", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 10))
        
        acceso_data = [
            ['Campo', 'Valor'],
            ['Acceso al sitio', racceso.acceso_sitio],
            ['Acceso para construcción', racceso.acceso_sitio_construccion],
            ['Longitud acceso sitio', f"{racceso.longitud_acceso_sitio} metros"],
            ['Longitud acceso construcción', f"{racceso.longitud_acceso_construccion} metros"],
            ['Tipo de suelo', racceso.tipo_suelo],
            ['Obstáculos', racceso.obstaculos],
            ['Trabajos adicionales', racceso.adicionales or 'Sin trabajos adicionales']
        ]
        
        acceso_table = Table(acceso_data, colWidths=[2.5*inch, 3.5*inch])
        acceso_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(acceso_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _generate_empalme_section(self, rempalme):
        """Genera la sección de información de empalme"""
        elements = []
        
        elements.append(Paragraph("INFORMACIÓN DE EMPALME", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 10))
        
        empalme_data = [
            ['Campo', 'Valor'],
            ['Latitud Empalme', str(rempalme.lat)],
            ['Longitud Empalme', str(rempalme.lon)],
            ['Proveedor de Energía', rempalme.proveedor],
            ['Capacidad de Energía', rempalme.capacidad],
            ['Comentarios', rempalme.comentarios or 'Sin comentarios']
        ]
        
        empalme_table = Table(empalme_data, colWidths=[2*inch, 4*inch])
        empalme_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(empalme_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def generate_summary_report(self):
        """
        Genera un informe resumido con estadísticas generales
        """
        registros = RegistrosTxTss.objects.filter(is_deleted=False)
        
        # Crear el buffer para el PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                               topMargin=72, bottomMargin=72)
        
        story = []
        
        # Título
        story.append(Paragraph("INFORME RESUMIDO DE REGISTROS TX/TSS", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Estadísticas generales
        total_registros = registros.count()
        registros_con_sitio = registros.filter(rsitio__isnull=False, rsitio__is_deleted=False).distinct().count()
        registros_con_acceso = registros.filter(racceso__isnull=False, racceso__is_deleted=False).distinct().count()
        registros_con_empalme = registros.filter(rempalme__isnull=False, rempalme__is_deleted=False).distinct().count()
        
        stats_data = [
            ['Métrica', 'Cantidad'],
            ['Total de registros', str(total_registros)],
            ['Registros con información de sitio', str(registros_con_sitio)],
            ['Registros con información de acceso', str(registros_con_acceso)],
            ['Registros con información de empalme', str(registros_con_empalme)],
            ['Porcentaje completitud sitio', f"{(registros_con_sitio/total_registros*100):.1f}%" if total_registros > 0 else "0%"],
            ['Porcentaje completitud acceso', f"{(registros_con_acceso/total_registros*100):.1f}%" if total_registros > 0 else "0%"],
            ['Porcentaje completitud empalme', f"{(registros_con_empalme/total_registros*100):.1f}%" if total_registros > 0 else "0%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 30))
        
        # Lista de registros
        story.append(Paragraph("LISTA DE REGISTROS", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        registros_list = [['Sitio', 'Usuario', 'Fecha', 'Sitio', 'Acceso', 'Empalme']]
        
        for registro in registros.select_related('sitio', 'user'):
            tiene_sitio = '✓' if registro.rsitio_set.filter(is_deleted=False).exists() else '✗'
            tiene_acceso = '✓' if registro.racceso_set.filter(is_deleted=False).exists() else '✗'
            tiene_empalme = '✓' if registro.rempalme_set.filter(is_deleted=False).exists() else '✗'
            
            registros_list.append([
                str(registro.sitio),
                str(registro.user),
                registro.created_at.strftime('%d/%m/%Y'),
                tiene_sitio,
                tiene_acceso,
                tiene_empalme
            ])
        
        registros_table = Table(registros_list, colWidths=[1.5*inch, 1.5*inch, 1*inch, 0.5*inch, 0.5*inch, 0.5*inch])
        registros_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(registros_table)
        
        # Construir el PDF
        doc.build(story)
        
        # Obtener el valor del buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Crear la respuesta HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="resumen_registros_txtss_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        response.write(pdf)
        
        return response 