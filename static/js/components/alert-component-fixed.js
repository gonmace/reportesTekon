/**
 * Alert Component - Versión corregida con delegación de eventos
 * Componente para mostrar alertas usando DaisyUI
 */

class AlertFixed {
    constructor() {
        this.alertContainer = null;
        this.initialized = false;
        this.pendingAlerts = [];
        this.confirmCallbacks = {};
    }

    init() {
        // Verificar que el DOM esté listo
        if (!document.body) {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.init());
                return;
            }
        }

        // Crear contenedor de alertas si no existe
        if (!document.getElementById('alerts-container')) {
            this.alertContainer = document.createElement('div');
            this.alertContainer.id = 'alerts-container';
            this.alertContainer.className = 'fixed top-4 right-4 z-[9999] space-y-2 max-w-sm';
            document.body.appendChild(this.alertContainer);
        } else {
            this.alertContainer = document.getElementById('alerts-container');
        }

        // Configurar delegación de eventos para el botón de cerrar
        this.setupEventDelegation();

        this.initialized = true;
        console.log('Alert component initialized with event delegation');

        // Procesar alertas pendientes
        this.pendingAlerts.forEach(alert => {
            this.show(alert.message, alert.type, alert.options);
        });
        this.pendingAlerts = [];
    }

    /**
     * Configura la delegación de eventos para el botón de cerrar
     */
    setupEventDelegation() {
        // Usar delegación de eventos en el contenedor
        this.alertContainer.addEventListener('click', (e) => {
            const closeBtn = e.target.closest('.alert-close-btn');
            if (closeBtn) {
                e.preventDefault();
                e.stopPropagation();
                
                const alertId = closeBtn.getAttribute('data-alert-id');
                console.log('Close button clicked via delegation for alert:', alertId);
                this.hide(alertId);
            }
        });

        // También manejar botones de confirmación
        this.alertContainer.addEventListener('click', (e) => {
            const confirmBtn = e.target.closest('.confirm-btn');
            if (confirmBtn) {
                e.preventDefault();
                e.stopPropagation();
                
                const confirmId = confirmBtn.getAttribute('data-confirm-id');
                const confirmed = confirmBtn.getAttribute('data-confirmed') === 'true';
                console.log('Confirm button clicked via delegation:', { confirmId, confirmed });
                this.handleConfirm(confirmId, confirmed);
            }
        });
    }

    /**
     * Muestra una alerta
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo de alerta: 'success', 'error', 'warning', 'info'
     * @param {object} options - Opciones adicionales
     */
    show(message, type = 'info', options = {}) {
        // Si no está inicializado, guardar la alerta para procesarla después
        if (!this.initialized) {
            this.pendingAlerts.push({ message, type, options });
            this.init();
            return `pending-${Date.now()}`;
        }

        const {
            autoHide = 0,
            id = `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            dismissible = true,
            icon = this.getDefaultIcon(type)
        } = options;

        console.log('Creating alert:', { id, type, message, dismissible });

        // Clases CSS según el tipo - Diseño minimalista
        const alertClasses = {
            success: 'bg-green-50 border-l-4 border-green-400 text-green-800',
            error: 'bg-red-50 border-l-4 border-red-400 text-red-800',
            warning: 'bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800',
            info: 'bg-blue-50 border-l-4 border-blue-400 text-blue-800'
        };

        // Crear elemento de alerta
        const alertElement = document.createElement('div');
        alertElement.id = id;
        alertElement.className = `${alertClasses[type] || alertClasses.info} p-4 rounded-r-lg shadow-sm border border-gray-200`;
        
        // Contenido de la alerta
        alertElement.innerHTML = `
            <div class="flex items-start">
                ${icon ? `<div class="flex-shrink-0 mr-3 mt-0.5">
                    <i class="${icon} text-sm"></i>
                </div>` : ''}
                <div class="flex-1">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                ${dismissible ? `
                    <div class="flex-shrink-0 ml-3">
                        <button type="button" class="alert-close-btn text-gray-400 hover:text-gray-600 transition-colors cursor-pointer" data-alert-id="${id}" style="background: none; border: none; padding: 4px;">
                            <i class="fa-solid fa-xmark text-xs"></i>
                        </button>
                    </div>
                ` : ''}
            </div>
        `;

        // Agregar animación de entrada
        alertElement.style.opacity = '0';
        alertElement.style.transform = 'translateX(100%)';
        alertElement.style.transition = 'all 0.3s ease-in-out';

        // Agregar al contenedor
        this.alertContainer.appendChild(alertElement);

        // Animar entrada
        setTimeout(() => {
            alertElement.style.opacity = '1';
            alertElement.style.transform = 'translateX(0)';
        }, 10);

        // Auto-ocultar si está configurado
        if (autoHide > 0) {
            setTimeout(() => {
                this.hide(id);
            }, autoHide);
        }

        return id;
    }

    /**
     * Oculta una alerta específica
     * @param {string} id - ID de la alerta a ocultar
     */
    hide(id) {
        console.log('Hiding alert:', id);
        const alertElement = document.getElementById(id);
        if (alertElement) {
            console.log('Alert element found, starting hide animation');
            // Animar salida
            alertElement.style.opacity = '0';
            alertElement.style.transform = 'translateX(100%)';
            
            setTimeout(() => {
                if (alertElement.parentNode) {
                    console.log('Removing alert element from DOM');
                    alertElement.parentNode.removeChild(alertElement);
                }
            }, 300);
        } else {
            console.error('Alert element not found for ID:', id);
        }
    }

    /**
     * Oculta todas las alertas
     */
    hideAll() {
        console.log('Hiding all alerts');
        const alerts = this.alertContainer.querySelectorAll('[id^="alert-"]');
        alerts.forEach(alert => {
            this.hide(alert.id);
        });
    }

    /**
     * Muestra una alerta de éxito
     * @param {string} message - Mensaje a mostrar
     * @param {object} options - Opciones adicionales
     */
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    /**
     * Muestra una alerta de error
     * @param {string} message - Mensaje a mostrar
     * @param {object} options - Opciones adicionales
     */
    error(message, options = {}) {
        return this.show(message, 'error', options);
    }

    /**
     * Muestra una alerta de advertencia
     * @param {string} message - Mensaje a mostrar
     * @param {object} options - Opciones adicionales
     */
    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    /**
     * Muestra una alerta informativa
     * @param {string} message - Mensaje a mostrar
     * @param {object} options - Opciones adicionales
     */
    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    /**
     * Obtiene el icono por defecto según el tipo
     * @param {string} type - Tipo de alerta
     * @returns {string} Clase del icono
     */
    getDefaultIcon(type) {
        const icons = {
            success: 'fa-solid fa-check-circle',
            error: 'fa-solid fa-exclamation-circle',
            warning: 'fa-solid fa-triangle-exclamation',
            info: 'fa-solid fa-circle-info'
        };
        return icons[type] || icons.info;
    }

    /**
     * Muestra una alerta de confirmación
     * @param {string} message - Mensaje a mostrar
     * @param {function} onConfirm - Función a ejecutar si se confirma
     * @param {function} onCancel - Función a ejecutar si se cancela
     * @param {object} options - Opciones adicionales
     */
    confirm(message, onConfirm, onCancel = null, options = {}) {
        const {
            id = `confirm-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            title = 'Confirmar',
            confirmText = 'Confirmar',
            cancelText = 'Cancelar'
        } = options;

        // Crear elemento de confirmación
        const confirmElement = document.createElement('div');
        confirmElement.id = id;
        confirmElement.className = 'bg-white border-l-4 border-blue-400 text-blue-800 p-4 rounded-r-lg shadow-sm border border-gray-200';
        
        confirmElement.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0 mr-3 mt-0.5">
                    <i class="fa-solid fa-question-circle text-sm"></i>
                </div>
                <div class="flex-1">
                    <h4 class="text-sm font-semibold mb-2">${title}</h4>
                    <p class="text-sm mb-3">${message}</p>
                    <div class="flex gap-2">
                        <button type="button" class="btn btn-sm btn-primary confirm-btn" data-confirm-id="${id}" data-confirmed="true">
                            ${confirmText}
                        </button>
                        <button type="button" class="btn btn-sm btn-ghost confirm-btn" data-confirm-id="${id}" data-confirmed="false">
                            ${cancelText}
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Guardar callbacks
        this.confirmCallbacks[id] = { onConfirm, onCancel };

        // Agregar al contenedor
        this.alertContainer.appendChild(confirmElement);

        // Animar entrada
        confirmElement.style.opacity = '0';
        confirmElement.style.transform = 'translateX(100%)';
        confirmElement.style.transition = 'all 0.3s ease-in-out';

        setTimeout(() => {
            confirmElement.style.opacity = '1';
            confirmElement.style.transform = 'translateX(0)';
        }, 10);

        return id;
    }

    /**
     * Maneja la respuesta de confirmación
     * @param {string} id - ID del elemento de confirmación
     * @param {boolean} confirmed - Si se confirmó o no
     */
    handleConfirm(id, confirmed) {
        const callbacks = this.confirmCallbacks[id];
        if (callbacks) {
            if (confirmed && callbacks.onConfirm) {
                callbacks.onConfirm();
            } else if (!confirmed && callbacks.onCancel) {
                callbacks.onCancel();
            }
            delete this.confirmCallbacks[id];
        }
        this.hide(id);
    }
}

// Crear instancia global
window.AlertFixed = new AlertFixed();

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.AlertFixed.init();
    });
} else {
    window.AlertFixed.init();
}
