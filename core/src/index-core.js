import DataTable from 'datatables.net-dt';
import Alert from './alerts.js';

document.addEventListener("DOMContentLoaded", function () {
    const sitiosTable = document.querySelector('#sitios-table');

    if (sitiosTable) {
        const isSuperuser = window.isSuperuser || false;

        const tabla = new DataTable('#sitios-table', {
            ajax: {
                url: '/api/v1/sitios/',
                dataSrc: ''  // DRF retorna lista directamente
            },
            columns: [
                { data: 'operator_id', className: 'text-center' },
                { data: 'pti_cell_id', className: 'whitespace-nowrap text-center' },
                { data: 'name', className: 'text-left w-fit max-w-40' },
                { data: 'region', className: 'text-left w-fit max-w-40' },
                { data: 'comuna', className: 'text-left w-fit max-w-40' },
                ...(isSuperuser ? [{
                    data: null,
                    orderable: false,
                    className: 'text-center',
                    render: function (data, type, row) {
                        return `
                            <a href="/sitios/${row.id}/editar/" class="text-info m-1" title="Editar sitio">
                                <i class="fa-regular fa-pen-to-square"></i>
                            </a>
                            <button 
                                type="button"
                                class="btn btn-ghost text-error m-1 eliminar-btn"
                                data-id="${row.id}" 
                                data-nombre="${row.name}"
                                title="Eliminar sitio"
                            >
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        `;
                    }
                }] : [])
            ],
            responsive: true,
            pageLength: 20,
            order: [[2, 'asc']],
            pagingType: 'simple_numbers',
            dom: 'rt<"flex justify-between items-center"<"info"i><"length"l><"pagination"p>>',
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
            autoWidth: false,
            bStateSave: true
        });

        // Buscador personalizado
        const buscador = document.getElementById('buscadorPersonalizado');
        if (buscador) {
            buscador.addEventListener('keyup', function () {
                tabla.search(this.value).draw();
            });
        }

        // Delegar evento para botón eliminar
        document.addEventListener("click", function (e) {
            const btn = e.target.closest(".eliminar-btn");
            if (!btn) return;

            e.preventDefault();

            const siteId = btn.dataset.id;
            const siteName = btn.dataset.nombre;

            // Usar el componente de alertas para confirmación
            Alert.confirm(
                `¿Estás seguro que deseas eliminar el sitio "${siteName}"?`,
                () => {
                    
                    // Usuario confirmó, proceder con la eliminación
                    fetch(`/api/v1/sitios/${siteId}/`, {
                        method: 'PUT',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({
                            'is_deleted': true
                        })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            Alert.success(data.message, { autoHide: 3000 });
                            tabla.ajax.reload(null, false);
                        } else {
                            Alert.error(data.message || 'Error al eliminar el sitio.');
                        }
                    })
                    .catch(error => {
                        console.error('Error al eliminar:', error);
                        Alert.error('Error de red o del servidor.');
                    });
                },
                () => {
                    // Usuario canceló, no hacer nada
                    console.log('Eliminación cancelada por el usuario');
                }
            );
        });

        // Función para obtener el CSRF Token desde cookies
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (const cookie of cookies) {
                    const trimmed = cookie.trim();
                    if (trimmed.startsWith(name + '=')) {
                        cookieValue = decodeURIComponent(trimmed.slice(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    }
});
