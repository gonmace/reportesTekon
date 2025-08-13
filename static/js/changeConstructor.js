// Usar la librería de alertas global
// La librería ya está disponible como window.Alert desde alert-component.js

// Función para cargar contratistas desde la API y poblar los selects
async function loadContractors() {
    try {
        const response = await fetch('/reg_construccion/api/v1/contractors/');
        if (response.ok) {
            const contractors = await response.json();
            populateContractorSelects(contractors);
        } else {
            throw new Error('Error al cargar contratistas');
        }
    } catch (error) {
        console.error('Error:', error);
        window.Alert.error('Error al cargar contratistas', {
            autoHide: 0,
            dismissible: true
        });
    }
}

function populateContractorSelects(contractors) {
    // Poblar todos los selects de constructor en la tabla
    const constructorSelects = document.querySelectorAll('.constructor-select');
    
    constructorSelects.forEach(select => {
        // Limpiar opciones existentes excepto la primera
        select.innerHTML = '<option value="">Seleccionar Constructor</option>';
        
        // Agregar opciones de contratistas
        contractors.forEach(contractor => {
            const option = document.createElement('option');
            option.value = contractor.id;
            option.textContent = `${contractor.name} (${contractor.code})`;
            select.appendChild(option);
        });
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", function () {
    if (!window.constructorInitialized) {
        window.constructorInitialized = true;
        loadContractors();
    }
});

// También ejecutar cuando la página esté completamente cargada
window.addEventListener("load", function () {
    setTimeout(function() {
        if (!window.constructorInitialized) {
            window.constructorInitialized = true;
            loadContractors();
        }
    }, 1000);
});

// Ejecutar cada segundo hasta que se encuentren los elementos
let checkIntervalConstructor = setInterval(function() {
    const constructorTexts = document.querySelectorAll('.constructor-text');
    if (constructorTexts.length > 0) {
        clearInterval(checkIntervalConstructor);
        // Solo inicializar una vez
        if (!window.constructorInitialized) {
            window.constructorInitialized = true;
            loadContractors();
        }
    }
}, 1000);
