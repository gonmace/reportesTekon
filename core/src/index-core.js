import DataTable from 'datatables.net-dt';

document.addEventListener("DOMContentLoaded", function(){
    // Verificar si existe la tabla de sitios
    const sitiosTable = document.querySelector('#sitios-table');
    if (sitiosTable) {
        // Obtener el valor de isSuperuser desde el template
        const isSuperuser = window.isSuperuser || false;
        
        const tabla = new DataTable('#sitios-table', {
            ajax: {
                url: '/sitios/api/',
                dataSrc: 'data'
            },
            columns: [
                { 
                    data: 'operator_id',
                    className: 'text-center'
                },
                { 
                    data: 'pti_cell_id',
                    className: 'whitespace-nowrap text-center'
                },
                { 
                    data: 'name',
                    className: 'text-left w-fit max-w-40'
                },
                { 
                    data: 'region',
                    className: 'text-left w-fit max-w-40'
                },
                { 
                    data: 'comuna',
                    className: 'text-left w-fit max-w-40'
                },
                ...(isSuperuser ? [{
                    data: null,
                    orderable: false,
                    className: 'text-center',
                    render: function(data, type, row) {
                        return `
                            <a href="/sitios/${row.id}/editar/" class="text-info m-1"><i class="fa-regular fa-pen-to-square"></i></a>
                            <a href="/sitios/${row.id}/eliminar/" class="text-error m-1"><i class="fa-solid fa-trash"></i></a>
                        `;
                    }
                }] : [])
            ],
            responsive: true,
            pageLength: 20,
            order: [[2, 'asc']], // Ordenar por nombre por defecto
            pagingType: 'simple_numbers',
            // Deshabilitar los estilos por defecto de DataTables y usar Tailwind
            // l = length, f = filter, r = processing, t = table, i = info, p = pagination
            dom: 'rt<"flex justify-between items-center"<"info"i><"length"l><"pagination"p>>',
            // Configurar clases de Tailwind para los elementos del DOM
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Buscar...",
                lengthMenu: "_MENU_ Registros",
                info: "_START_ al _END_ de _TOTAL_ ",
                infoEmpty: "0 al 0 de 0",
                infoFiltered: "(filtrado de _MAX_ )",
                paginate: {
                    first: "<<",
                    previous: "<",
                    next: ">",
                    last: ">>"
                }
            },
            // Deshabilitar estilos por defecto
            autoWidth: false,
            bStateSave: true,

        });
        // Estilos para el buscador
        $('#buscadorPersonalizado').on('keyup', function () {
            tabla.search(this.value).draw();
        });
    }
});
