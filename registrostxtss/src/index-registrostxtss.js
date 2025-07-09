import DataTableUtils from './datatable.js';

// Función de utilidad para mostrar alertas
function showAlert(message, type = 'info', options = {}) {
    // Verificar si el componente de alertas está disponible
    if (window.Alert && typeof window.Alert.show === 'function') {
        return window.Alert.show(message, type, options);
    } else {
        // Fallback a alert nativo
        const iconMap = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        const icon = iconMap[type] || iconMap.info;
        alert(`${icon} ${message}`);
        return null;
    }
}

// Función de utilidad para alertas de éxito
function showSuccess(message, options = {}) {
    return showAlert(message, 'success', options);
}

// Función de utilidad para alertas de error
function showError(message, options = {}) {
    return showAlert(message, 'error', options);
}

document.addEventListener("DOMContentLoaded", function () {

    // Cargar Registros usando la función reutilizable de datatable.js
    if (window.DataTableUtils && window.DataTableUtils.createRegistrosTable) {
        // Primero hacer el fetch para obtener los datos
        fetch('/api/v1/registros/')
        .then(response => response.json())
        .then(data => {
            console.log('Datos recibidos:', data);
            
            // Luego crear la tabla con los datos recibidos
            const registrosTable = window.DataTableUtils.createRegistrosTable('#sitios-table', data);
            
            // Guardar referencia global para uso posterior
            window.registrosTable = registrosTable;
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Error al cargar los registros. Por favor, inténtalo de nuevo.');
        });
    } else {
        console.error('DataTableUtils no está disponible. Asegúrate de que datatable.js esté cargado.');
        
        // Fallback al método original
        fetch('/api/v1/registros/')
        .then(response => response.json())
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Activar el modal
    const modal = document.getElementById("activar-registro-modal");
    const activarBtn = document.getElementById("activar-registro-btn");

    if (activarBtn && modal) {
        activarBtn.addEventListener("click", function () {
            console.log("activarBtn");
            
            modal.showModal();
        });
    }

    window.closeModal = function () {
        modal.close();
    };

    const activarRegistroBtn = document.getElementById("activar-registro-btn");
    if (activarRegistroBtn) {
        activarRegistroBtn.addEventListener("click", function () {
            console.log("activarRegistroBtn");
        });
    }

    // Activar el registro
    // Interceptar el submit del formulario
    const form = document.querySelector('#activar-registro-modal form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = {
                sitio_id: formData.get('sitio'),
                user_id: formData.get('user'),
                registro0: false
            };

            // Obtener el token CSRF
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Hacer la petición POST a la API
            fetch('/api/v1/registros/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Error en la petición');
                }
            })
            .then(data => {
                console.log('Registro creado exitosamente:', data);
                
                // Cerrar el modal
                modal.close();
                
                // Mostrar alerta de éxito
                showSuccess('Registro creado exitosamente', {
                    autoHide: 5000, // Auto-ocultar después de 5 segundos
                    dismissible: true
                });
                
                // Recargar la página después de un breve delay para que se vea la alerta
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Mostrar alerta de error
                showError('Error al crear el registro. Por favor, inténtalo de nuevo.', {
                    autoHide: 0, // No auto-ocultar
                    dismissible: true
                });
            });
        });
    }
});
