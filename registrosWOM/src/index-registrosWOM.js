import DataTable from 'datatables.net-dt';

document.addEventListener("DOMContentLoaded", function () {
    const sitiosTable = document.querySelector('#sitios-table');

    if (sitiosTable) {
        const isSuperuser = window.isSuperuser || false;

        const tabla = new DataTable('#sitios-table', {
            ajax: {
                url: '/api/v1/registros/',
                dataSrc: ''  // DRF retorna lista directamente
            },
            columns: [
                { data: 'pti_cell_id', className: 'whitespace-nowrap text-center' },
                { data: 'operator_id', className: 'text-center' },
                { data: 'name', className: 'text-left w-fit max-w-40' },
                { 
                    data: 'user',
                    className: 'text-left w-fit max-w-40',
                    render: function(data, type, row) {
                        // Handle nested user object
                        if (data && data.username) {
                            return data.username;
                        }
                        return 'Sin asignar';
                    }
                },
                { 
                    data: null,
                    className: 'text-center',
                    render: function(data, type, row) {
                        return '<button class="btn btn-primary btn-sm crear-registro-btn" data-id="' + row.id + '">Crear</button>';
                    }
                },
            ],
            responsive: true,
            // scrollX: true,
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
                infoFiltered: "(filtrado de _MAX_ registros)",
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

        // Modal de edición
        const modal = document.getElementById('edit_site_modal');
        const modalContent = document.getElementById('modal-content');

        // Función para convertir string a número de forma segura
        function safeParseFloat(value) {
            if (!value || value.trim() === '') {
                return null;
            }
            // Asegurar que se use punto decimal
            const cleanValue = value.toString().replace(',', '.').trim();
            const parsed = parseFloat(cleanValue);
            return isNaN(parsed) ? null : parsed;
        }

        // Función para formatear número con punto decimal
        function formatDecimal(value) {
            if (value === null || value === undefined || value === '') {
                return '';
            }
            // Convertir a número y formatear con punto decimal
            const num = parseFloat(value.toString().replace(',', '.'));
            return isNaN(num) ? '' : num.toFixed(6);
        }

        // Función para abrir el modal de edición
        function openEditModal(siteId) {
            fetch(`/api/v1/sitios/${siteId}/edit-modal/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Usar el HTML renderizado del servidor
                    modalContent.innerHTML = data.form_html;
                    modal.showModal();

                    // Asegurar que los campos de coordenadas usen punto decimal
                    const latInput = modalContent.querySelector('input[name="lat_base"]');
                    const lonInput = modalContent.querySelector('input[name="lon_base"]');
                    
                    if (latInput && latInput.value) {
                        latInput.value = formatDecimal(latInput.value);
                    }
                    if (lonInput && lonInput.value) {
                        lonInput.value = formatDecimal(lonInput.value);
                    }

                    // Manejar el envío del formulario
                    const form = document.getElementById('edit-site-form');
                    form.addEventListener('submit', function(e) {
                        e.preventDefault();
                        
                        const formData = new FormData(form);
                        const data = {};
                        formData.forEach((value, key) => {
                            // Manejar valores decimales correctamente
                            if (key === 'lat_base' || key === 'lon_base') {
                                data[key] = safeParseFloat(value);
                            } else {
                                data[key] = value;
                            }
                        });

                        fetch(`/api/v1/sitios/${siteId}/edit-modal/`, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken'),
                                'Content-Type': 'application/json',
                                'Accept': 'application/json'
                            },
                            body: JSON.stringify(data)
                        })
                        .then(res => res.json())
                        .then(data => {
                            if (data.success) {
                                Alert.success(data.message, { autoHide: 3000 });
                                modal.close();
                                tabla.ajax.reload(null, false);
                            } else {
                                Alert.error(data.message || 'Error al actualizar el sitio.');
                            }
                        })
                        .catch(error => {
                            console.error('Error al actualizar:', error);
                            Alert.error('Error de red o del servidor.');
                        });
                    });
                } else {
                    Alert.error('Error al cargar los datos del sitio.');
                }
            })
            .catch(error => {
                console.error('Error al cargar sitio:', error);
                Alert.error('Error de red o del servidor.');
            });
        }

        // Función para cerrar el modal
        window.closeModal = function() {
            modal.close();
        };

        // Delegar evento para botón editar
        document.addEventListener("click", function (e) {
            const btn = e.target.closest(".editar-btn");
            if (btn) {
                e.preventDefault();
                const siteId = btn.dataset.id;
                openEditModal(siteId);
            }
        });

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

        // Delegar evento para botón crear registro
        document.addEventListener("click", function (e) {
            const btn = e.target.closest(".crear-registro-btn");
            if (!btn) return;

            e.preventDefault();

            const siteId = btn.dataset.id;
            
            // Aquí puedes agregar la lógica para crear el registro
            // Por ejemplo, abrir un modal o redirigir a una página
            console.log('Crear registro para sitio ID:', siteId);
            
            // Ejemplo: redirigir a una página de creación
            // window.location.href = `/registros/crear/${siteId}/`;
            
            // Redirigir a la página de creación
            window.location.href = `/createReg0.html?siteId=${siteId}`;
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
