// Importar el componente Alert desde el script global
const Alert = window.Alert;

document.addEventListener("DOMContentLoaded", function () {
        
    // Cargar usuarios ITO
    loadUsersIto();
    
    // Manejar el envío del formulario
    const form = document.getElementById('create-registro-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

async function loadUsersIto() {
    try {
        const response = await fetch('/txtss/api/v1/registros/usuarios_ito/');
        if (response.ok) {
            const users = await response.json();
            populateUserSelect(users);
        } else {
            throw new Error('Error al cargar usuarios ITO');
        }
    } catch (error) {
        console.error('Error:', error);
        Alert.error('Error al cargar usuarios ITO', {
            autoHide: 0,
            dismissible: true
        });
    }
}

function populateUserSelect(users) {
    const userSelect = document.getElementById('user-select');
    if (userSelect) {
        // Limpiar opciones existentes excepto la primera
        userSelect.innerHTML = '<option value="">Seleccionar ITO</option>';
        
        // Agregar opciones de usuarios
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = `${user.username} - ${user.first_name} ${user.last_name}`;
            userSelect.appendChild(option);
        });
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const user_id = formData.get('user_id');
    const registro = formData.get('registro') === 'on';
    
    if (!user_id) {
        Alert.error('Por favor selecciona un ITO', {
            autoHide: 3000,
            dismissible: true
        });
        return;
    }
    
    const data = {
        sitio_id: parseInt(window.siteId),
        user_id: parseInt(user_id),
        registro: registro
    };
    
    // Obtener el token CSRF
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    try {
        const response = await fetch('/txtss/api/v1/registros/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Registro creado exitosamente:', result);
            
            Alert.success('Registro creado exitosamente', {
                autoHide: 3000,
                dismissible: true
            });
            
            // Redirigir a la página de listado después de un breve delay
            setTimeout(() => {
                window.location.href = '/registros/';
            }, 1500);
        } else {
            const errorData = await response.json();
            let errorMessage = 'Error al crear el registro. Por favor, inténtalo de nuevo.';
            
            if (errorData.errors && errorData.errors.non_field_errors) {
                errorMessage = errorData.errors.non_field_errors[0];
            } else if (errorData.message) {
                errorMessage = errorData.message;
            }
            
            Alert.error(errorMessage, {
                autoHide: 0,
                dismissible: true
            });
        }
    } catch (error) {
        console.error('Error:', error);
        Alert.error('Error al crear el registro. Por favor, inténtalo de nuevo.', {
            autoHide: 0,
            dismissible: true
        });
    }
} 