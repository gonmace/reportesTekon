// Usar la librería de alertas global
// La librería ya está disponible como window.Alert desde alert-component.js

// Función para cargar usuarios ITO desde la API y poblar los selects
async function loadUsersIto() {
    try {
        const response = await fetch('/reg_construccion/api/v1/users_ito/');
        if (response.ok) {
            const users = await response.json();
            populateUserSelects(users);
        } else {
            throw new Error('Error al cargar usuarios ITO');
        }
    } catch (error) {
        console.error('Error:', error);
        window.Alert.error('Error al cargar usuarios ITO', {
            autoHide: 0,
            dismissible: true
        });
    }
}

function populateUserSelects(users) {
    // Poblar todos los selects de ITO en la tabla
    const itoSelects = document.querySelectorAll('.ito-select');
    
    itoSelects.forEach(select => {
        // Limpiar opciones existentes excepto la primera
        select.innerHTML = '<option value="">Seleccionar ITO</option>';
        
        // Agregar opciones de usuarios
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = `${user.username}${user.first_name ? ` (${user.first_name} ${user.last_name || ''})` : ''}`;
            select.appendChild(option);
        });
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", function () {
    if (!window.itoInitialized) {
        window.itoInitialized = true;
        loadUsersIto();
    }
});

// También ejecutar cuando la página esté completamente cargada
window.addEventListener("load", function () {
    setTimeout(function() {
        if (!window.itoInitialized) {
            window.itoInitialized = true;
            loadUsersIto();
        }
    }, 1000);
});

// Ejecutar cada segundo hasta que se encuentren los elementos
let checkIntervalIto = setInterval(function() {
    const itoTexts = document.querySelectorAll('.ito-text');
    if (itoTexts.length > 0) {
        clearInterval(checkIntervalIto);
        // Solo inicializar una vez
        if (!window.itoInitialized) {
            window.itoInitialized = true;
            loadUsersIto();
        }
    }
}, 1000);
