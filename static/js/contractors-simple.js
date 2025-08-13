// Funcionalidad para la gestión de contratistas (versión simple)
console.log('Script de contratistas cargado');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado, inicializando contratistas...');
    
    const contractorsTable = document.querySelector('#contractors-table');
    const addContractorBtn = document.querySelector('#addContractorBtn');
    const contractorModal = document.querySelector('#contractorModal');
    const modalTitle = document.querySelector('#modalTitle');
    const modalContent = document.querySelector('#modalContent');
    const saveContractorBtn = document.querySelector('#saveContractorBtn');
    const cancelContractorBtn = document.querySelector('#cancelContractorBtn');

    console.log('Elementos encontrados:', {
        contractorsTable: !!contractorsTable,
        addContractorBtn: !!addContractorBtn,
        contractorModal: !!contractorModal,
        modalTitle: !!modalTitle,
        modalContent: !!modalContent,
        saveContractorBtn: !!saveContractorBtn,
        cancelContractorBtn: !!cancelContractorBtn
    });

    let currentContractorId = null;
    let tabla = null;

    // Función para obtener CSRF token
    function getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // Función para mostrar alerta
    function showAlert(type, message) {
        console.log('showAlert:', type, message);
        // Usar la función de alerta global si existe
        if (typeof window.showAlert === 'function') {
            window.showAlert(type, message);
        } else {
            alert(`${type}: ${message}`);
        }
    }

    // Función para validar formulario en tiempo real
    function validateForm() {
        const form = document.querySelector('#contractorForm');
        if (!form) return false;

        const nameField = form.querySelector('[name="name"]');
        const codeField = form.querySelector('[name="code"]');
        let isValid = true;

        // Limpiar errores previos
        clearFormErrors();

        // Validar nombre solo si el usuario ha interactuado con el campo
        if (nameField.dataset.touched === 'true') {
            if (!nameField.value.trim()) {
                showFieldError(nameField, 'El nombre es obligatorio');
                isValid = false;
            } else if (nameField.value.trim().length < 3) {
                showFieldError(nameField, 'El nombre debe tener al menos 3 caracteres');
                isValid = false;
            }
        }

        // Validar código solo si el usuario ha interactuado con el campo
        if (codeField.dataset.touched === 'true') {
            if (!codeField.value.trim()) {
                showFieldError(codeField, 'El código es obligatorio');
                isValid = false;
            } else if (codeField.value.trim().length < 2) {
                showFieldError(codeField, 'El código debe tener al menos 2 caracteres');
                isValid = false;
            }
        }

        // Actualizar estado del botón
        updateSaveButtonState(isValid);

        return isValid;
    }

    // Función para validar formulario completo (para envío)
    function validateFormForSubmit() {
        const form = document.querySelector('#contractorForm');
        if (!form) return false;

        const nameField = form.querySelector('[name="name"]');
        const codeField = form.querySelector('[name="code"]');
        let isValid = true;

        // Limpiar errores previos
        clearFormErrors();

        // Validar nombre (siempre para envío)
        if (!nameField.value.trim()) {
            showFieldError(nameField, 'El nombre es obligatorio');
            isValid = false;
        } else if (nameField.value.trim().length < 3) {
            showFieldError(nameField, 'El nombre debe tener al menos 3 caracteres');
            isValid = false;
        }

        // Validar código (siempre para envío)
        if (!codeField.value.trim()) {
            showFieldError(codeField, 'El código es obligatorio');
            isValid = false;
        } else if (codeField.value.trim().length < 2) {
            showFieldError(codeField, 'El código debe tener al menos 2 caracteres');
            isValid = false;
        }

        // Actualizar estado del botón
        updateSaveButtonState(isValid);

        return isValid;
    }

    // Función para mostrar error en campo específico
    function showFieldError(field, message) {
        // Agregar clase de error de DaisyUI
        field.classList.add('input-error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error mt-2';
        errorDiv.innerHTML = `
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
            <div class="text-sm">${message}</div>
        `;
        
        field.parentNode.appendChild(errorDiv);
    }

    // Función para limpiar errores del formulario
    function clearFormErrors() {
        const form = document.querySelector('#contractorForm');
        if (!form) return;

        // Limpiar clases de error de DaisyUI
        form.querySelectorAll('.input-error').forEach(field => {
            field.classList.remove('input-error');
        });

        // Remover mensajes de error
        form.querySelectorAll('.alert-error').forEach(alert => {
            alert.remove();
        });
    }

    // Función para actualizar estado del botón guardar
    function updateSaveButtonState(isValid) {
        if (saveContractorBtn) {
            saveContractorBtn.disabled = !isValid;
            saveContractorBtn.classList.toggle('btn-disabled', !isValid);
        }
    }

    // Función para guardar contratista
    function saveContractor() {
        console.log('saveContractor llamado');
        
        if (!validateFormForSubmit()) {
            showAlert('error', 'Por favor, corrige los errores en el formulario');
            return;
        }

        const form = document.querySelector('#contractorForm');
        if (!form) {
            console.error('No se encontró el formulario');
            return;
        }
        
        // Mostrar loading en el botón
        const originalText = saveContractorBtn.innerHTML;
        saveContractorBtn.innerHTML = `
            <svg class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            Guardando...
        `;
        saveContractorBtn.disabled = true;
        
        const formData = new FormData(form);
        
        const url = currentContractorId ? 
            `/api/v1/contractors/${currentContractorId}/edit-modal/` : 
            '/api/v1/contractors/create-modal/';
        
        console.log('URL para guardar:', url);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Accept': 'application/json'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta de guardar:', data);
            if (data.success) {
                showAlert('success', data.message);
                contractorModal.close();
                // Recargar la tabla de contratistas
                loadContractors();
            } else {
                showAlert('error', data.message);
                // Mostrar errores en el formulario
                if (data.errors) {
                    Object.keys(data.errors).forEach(field => {
                        const fieldElement = form.querySelector(`[name="${field}"]`);
                        if (fieldElement) {
                            showFieldError(fieldElement, data.errors[field].join(', '));
                        }
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error al guardar:', error);
            showAlert('error', 'Error al guardar el contratista');
        })
        .finally(() => {
            // Restaurar botón
            saveContractorBtn.innerHTML = originalText;
            saveContractorBtn.disabled = false;
        });
    }

    // Función para cargar formulario de contratista
    function loadContractorForm(contractorId = null, nombre = null) {
        console.log('loadContractorForm llamado con:', { contractorId, nombre });
        
        // Mostrar loading en el modal
        modalContent.innerHTML = `
            <div class="flex items-center justify-center py-8">
                <div class="loading loading-spinner loading-lg text-primary"></div>
                <span class="ml-3 text-base-content">Cargando formulario...</span>
            </div>
        `;
        
        const url = contractorId ? 
            `/api/v1/contractors/${contractorId}/edit-modal/` : 
            '/api/v1/contractors/create-modal/';
        
        console.log('URL:', url);
        
        fetch(url, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Accept': 'application/json'
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.success) {
                modalContent.innerHTML = data.form_html;
                modalTitle.textContent = contractorId ? `Editar Contratista: ${nombre}` : 'Agregar Contratista';
                currentContractorId = contractorId;
                contractorModal.showModal();
                
                // Agregar event listeners al formulario
                const form = document.querySelector('#contractorForm');
                if (form) {
                    // Event listener para submit
                    form.addEventListener('submit', function(e) {
                        e.preventDefault();
                        saveContractor();
                    });

                    // Event listeners para validación en tiempo real
                    const nameField = form.querySelector('[name="name"]');
                    const codeField = form.querySelector('[name="code"]');

                    if (nameField) {
                        // Marcar como tocado cuando el usuario interactúa
                        nameField.addEventListener('blur', function() {
                            this.dataset.touched = 'true';
                            validateForm();
                        });
                        
                        // Validar en tiempo real solo si ya fue tocado
                        nameField.addEventListener('input', function() {
                            if (this.dataset.touched === 'true') {
                                validateForm();
                            }
                        });
                    }

                    if (codeField) {
                        // Marcar como tocado cuando el usuario interactúa
                        codeField.addEventListener('blur', function() {
                            this.dataset.touched = 'true';
                            validateForm();
                        });
                        
                        // Validar en tiempo real solo si ya fue tocado
                        codeField.addEventListener('input', function() {
                            if (this.dataset.touched === 'true') {
                                validateForm();
                            }
                        });
                    }

                    // No validar al inicio, solo marcar el botón como habilitado
                    updateSaveButtonState(true);
                }
            } else {
                showAlert('error', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('error', 'Error al cargar el formulario');
        });
    }

    // Función para cargar contratistas
    function loadContractors() {
        console.log('Cargando contratistas...');
        
        if (!contractorsTable) {
            console.error('No se encontró la tabla de contratistas');
            return;
        }

        // Mostrar loading en la tabla
        contractorsTable.querySelector('tbody').innerHTML = `
            <tr>
                <td colspan="4" class="text-center py-8">
                    <div class="flex items-center justify-center">
                        <div class="loading loading-spinner loading-lg text-primary"></div>
                        <span class="ml-3 text-base-content">Cargando contratistas...</span>
                    </div>
                </td>
            </tr>
        `;

        fetch('/api/v1/contractors/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Accept': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Contratistas cargados:', data);
            renderContractorsTable(data);
        })
        .catch(error => {
            console.error('Error al cargar contratistas:', error);
            contractorsTable.querySelector('tbody').innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-8">
                        <div class="alert alert-error">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                            </svg>
                            <span>Error al cargar los contratistas</span>
                        </div>
                    </td>
                </tr>
            `;
        });
    }

    // Función para renderizar la tabla de contratistas
    function renderContractorsTable(contractors) {
        if (!contractorsTable) return;

        const tbody = contractorsTable.querySelector('tbody');
        
        if (contractors.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-8">
                        <div class="flex flex-col items-center space-y-4">
                            <svg class="w-16 h-16 text-base-content/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                            </svg>
                            <div class="text-base-content/70">
                                <h3 class="text-lg font-semibold mb-2">No hay contratistas</h3>
                                <p class="text-sm">Comienza agregando tu primer contratista</p>
                            </div>
                            <button id="addFirstContractorBtn" class="btn btn-primary btn-sm">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                                </svg>
                                Agregar Contratista
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            
            // Event listener para el botón de agregar primer contratista
            const addFirstBtn = document.querySelector('#addFirstContractorBtn');
            if (addFirstBtn) {
                addFirstBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    loadContractorForm();
                });
            }
            return;
        }

        tbody.innerHTML = contractors.map(contractor => `
            <tr class="hover:bg-base-200 transition-colors">
                <td class="py-4">
                    <div class="flex items-center space-x-3">
                        <div class="bg-primary text-primary-content rounded-full w-10 h-10 flex items-center justify-center">
                            <span class="text-sm font-semibold">${contractor.name.charAt(0).toUpperCase()}</span>
                        </div>
                        <div>
                            <div class="font-semibold text-base-content">${contractor.name}</div>
                            <div class="text-sm text-base-content/70">Creado: ${contractor.created_at}</div>
                        </div>
                    </div>
                </td>
                <td class="text-center">
                    <div class="badge badge-primary badge-lg">${contractor.code}</div>
                </td>
                <td class="text-center">
                    ${contractor.is_active ? 
                        '<span class="badge badge-success badge-lg">Activo</span>' : 
                        '<span class="badge badge-error badge-lg">Inactivo</span>'
                    }
                </td>
                <td class="text-center">
                    <div class="flex items-center justify-center space-x-2">
                        <button onclick="editContractor(${contractor.id}, '${contractor.name}')" class="btn btn-sm btn-ghost btn-circle" title="Editar contratista">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button onclick="deleteContractor(${contractor.id}, '${contractor.name}')" class="btn btn-sm btn-ghost btn-circle text-error hover:bg-error hover:text-error-content" title="Eliminar contratista">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // Event listeners
    console.log('Configurando event listeners...');
    if (addContractorBtn) {
        console.log('Agregando event listener al botón agregar');
        addContractorBtn.addEventListener('click', function(e) {
            console.log('Botón agregar contratista clickeado');
            e.preventDefault();
            loadContractorForm();
        });
    } else {
        console.error('No se encontró el botón addContractorBtn');
    }

    // Event listeners para botones del modal
    if (saveContractorBtn) {
        saveContractorBtn.addEventListener('click', function(e) {
            console.log('Botón guardar clickeado');
            e.preventDefault();
            saveContractor();
        });
    }

    if (cancelContractorBtn) {
        cancelContractorBtn.addEventListener('click', function(e) {
            console.log('Botón cancelar clickeado');
            e.preventDefault();
            contractorModal.close();
        });
    }

    // Cerrar modal al hacer clic fuera
    if (contractorModal) {
        contractorModal.addEventListener('click', (e) => {
            if (e.target === contractorModal) {
                contractorModal.close();
            }
        });

        // Event listener para cuando se cierra el modal
        contractorModal.addEventListener('close', () => {
            // Limpiar formulario y errores
            const form = document.querySelector('#contractorForm');
            if (form) {
                form.reset();
                clearFormErrors();
            }
            currentContractorId = null;
        });
    }

    // Función para editar contratista (para usar desde la tabla)
    window.editContractor = function(contractorId, nombre) {
        loadContractorForm(contractorId, nombre);
    };

    // Función para eliminar contratista (para usar desde la tabla)
    window.deleteContractor = function(contractorId, nombre) {
        if (confirm(`¿Estás seguro de que quieres eliminar el contratista "${nombre}"?`)) {
            // Mostrar loading
            showAlert('info', 'Eliminando contratista...');
            
            fetch(`/api/v1/contractors/${contractorId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Accept': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', data.message);
                    loadContractors(); // Recargar tabla
                } else {
                    showAlert('error', data.message);
                }
            })
            .catch(error => {
                console.error('Error al eliminar:', error);
                showAlert('error', 'Error al eliminar el contratista');
            });
        }
    };

    // Cargar contratistas al cargar la página
    loadContractors();

    console.log('Inicialización de contratistas completada');
});
