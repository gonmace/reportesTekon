from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Q
from registrostxtss.models import RegistrosTxTss
from registrostxtss.services.pdf_report_service import PDFReportService
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Genera informes en PDF de registros Tx/Tss'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            type=str,
            choices=['completo', 'resumen'],
            default='completo',
            help='Tipo de informe a generar (completo o resumen)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Ruta del archivo de salida (opcional)'
        )
        
        parser.add_argument(
            '--sitio-id',
            type=int,
            help='ID del sitio para filtrar registros'
        )
        
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID del usuario para filtrar registros'
        )
        
        parser.add_argument(
            '--fecha-inicio',
            type=str,
            help='Fecha de inicio (YYYY-MM-DD)'
        )
        
        parser.add_argument(
            '--fecha-fin',
            type=str,
            help='Fecha de fin (YYYY-MM-DD)'
        )
        
        parser.add_argument(
            '--completitud',
            type=str,
            choices=['completo', 'incompleto'],
            help='Filtrar por completitud'
        )
        
        parser.add_argument(
            '--list-only',
            action='store_true',
            help='Solo listar registros sin generar PDF'
        )

    def handle(self, *args, **options):
        try:
            # Construir el queryset base
            registros = RegistrosTxTss.objects.filter(is_deleted=False)
            
            # Aplicar filtros
            if options['sitio_id']:
                registros = registros.filter(sitio_id=options['sitio_id'])
                self.stdout.write(f"Filtrando por sitio ID: {options['sitio_id']}")
            
            if options['user_id']:
                registros = registros.filter(user_id=options['user_id'])
                self.stdout.write(f"Filtrando por usuario ID: {options['user_id']}")
            
            if options['fecha_inicio']:
                registros = registros.filter(created_at__date__gte=options['fecha_inicio'])
                self.stdout.write(f"Filtrando desde fecha: {options['fecha_inicio']}")
            
            if options['fecha_fin']:
                registros = registros.filter(created_at__date__lte=options['fecha_fin'])
                self.stdout.write(f"Filtrando hasta fecha: {options['fecha_fin']}")
            
            if options['completitud']:
                if options['completitud'] == 'completo':
                    registros = registros.filter(
                        rsitio__isnull=False,
                        racceso__isnull=False,
                        rempalme__isnull=False
                    ).distinct()
                elif options['completitud'] == 'incompleto':
                    registros = registros.filter(
                        Q(rsitio__isnull=True) |
                        Q(racceso__isnull=True) |
                        Q(rempalme__isnull=True)
                    ).distinct()
                self.stdout.write(f"Filtrando por completitud: {options['completitud']}")
            
            # Mostrar estadísticas
            total_registros = registros.count()
            self.stdout.write(f"Total de registros encontrados: {total_registros}")
            
            if total_registros == 0:
                self.stdout.write(self.style.WARNING("No se encontraron registros con los filtros aplicados."))
                return
            
            # Solo listar si se solicita
            if options['list_only']:
                self.stdout.write("\nLista de registros:")
                self.stdout.write("-" * 80)
                for registro in registros.select_related('sitio', 'user')[:10]:  # Mostrar solo los primeros 10
                    self.stdout.write(f"ID: {registro.id} | Sitio: {registro.sitio} | Usuario: {registro.user} | Fecha: {registro.created_at.strftime('%d/%m/%Y %H:%M')}")
                if total_registros > 10:
                    self.stdout.write(f"... y {total_registros - 10} registros más")
                return
            
            # Generar el informe
            self.stdout.write(f"Generando informe {options['tipo']}...")
            
            pdf_service = PDFReportService()
            
            if options['tipo'] == 'resumen':
                response = pdf_service.generate_summary_report()
            else:
                response = pdf_service.generate_complete_report(registros)
            
            # Determinar la ruta de salida
            if options['output']:
                output_path = options['output']
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"informe_registros_txtss_{options['tipo']}_{timestamp}.pdf"
                output_path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
                
                # Crear directorio si no existe
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Guardar el archivo
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Informe generado exitosamente: {output_path}"
                )
            )
            
            # Mostrar estadísticas del informe
            self.stdout.write(f"\nEstadísticas del informe:")
            self.stdout.write(f"- Total de registros: {total_registros}")
            self.stdout.write(f"- Tamaño del archivo: {os.path.getsize(output_path) / 1024:.1f} KB")
            
        except Exception as e:
            raise CommandError(f"Error al generar el informe: {str(e)}") 