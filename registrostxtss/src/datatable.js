// Función reutilizable para crear tabla HTML nativa
function initializeDataTable(selector, options = {}) {
    const defaultOptions = {
        pageSize: 10,
        sortable: true,
        searchable: true
    };

    // Combinar opciones por defecto con las opciones personalizadas
    const finalOptions = { ...defaultOptions, ...options };

    // Obtener el elemento de la tabla
    const tableElement = document.querySelector(selector);
    if (!tableElement) {
        throw new Error(`No se encontró el elemento con selector: ${selector}`);
    }

    // Crear objeto de tabla personalizado
    const table = {
        element: tableElement,
        options: finalOptions,
        data: [],
        currentPage: 1,
        pageSize: finalOptions.pageSize,
        
        // Método para limpiar tabla
        clear: function() {
            const tbody = this.element.querySelector('tbody');
            if (tbody) {
                tbody.innerHTML = '';
            }
        },
        
        // Método para agregar fila
        addRow: function(rowData) {
            const tbody = this.element.querySelector('tbody');
            if (!tbody) {
                const newTbody = document.createElement('tbody');
                this.element.appendChild(newTbody);
            }
            
            const row = document.createElement('tr');
            rowData.forEach(cellData => {
                const cell = document.createElement('td');
                cell.innerHTML = cellData;
                row.appendChild(cell);
            });
            tbody.appendChild(row);
        },
        
        // Método para redibujar tabla
        draw: function() {
            // Implementación básica - la tabla se actualiza automáticamente
            console.log('Tabla redibujada');
        }
    };

    return table;
}

// Función para cargar datos en la tabla
function loadTableData(table, data, columns) {
    // Limpiar tabla existente
    table.clear();

    // Agregar datos
    data.forEach(item => {
        const row = [];
        columns.forEach(column => {
            if (typeof column === 'string') {
                row.push(item[column]);
            } else if (typeof column === 'function') {
                row.push(column(item));
            } else if (column.key) {
                row.push(column.render ? column.render(item[column.key], item) : item[column.key]);
            }
        });
        table.addRow(row);
    });

    // Redibujar tabla
    table.draw();
}

// Función para actualizar tabla con datos de la API
function updateTableFromAPI(table, apiUrl, columns, options = {}) {
    const defaultOptions = {
        showLoading: true,
        onSuccess: null,
        onError: null
    };

    const finalOptions = { ...defaultOptions, ...options };

    if (finalOptions.showLoading) {
        // Mostrar indicador de carga
        showAlert('Cargando datos...', 'info');
    }

    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loadTableData(table, data, columns);
            
            if (finalOptions.onSuccess) {
                finalOptions.onSuccess(data);
            }
        })
        .catch(error => {
            console.error('Error cargando datos:', error);
            
            if (finalOptions.onError) {
                finalOptions.onError(error);
            } else {
                showError('Error al cargar los datos. Por favor, inténtalo de nuevo.');
            }
        });
}

// Función para crear tabla de registros
function createRegistrosTable(selector, data) {
    const columns = [
        { key: 'id', render: (value) => `<strong>#${value}</strong>` },
        { key: 'sitio', render: (value, item) => item.sitio?.name || 'N/A' },
        { key: 'user', render: (value, item) => item.user?.username || 'N/A' },
        { 
            key: 'registro0', 
            render: (value) => value ? 
                '<span class="badge bg-success">Activo</span>' : 
                '<span class="badge bg-secondary">Inactivo</span>'
        },
        { 
            key: 'created_at', 
            render: (value) => new Date(value).toLocaleString('es-ES')
        },
        {
            key: 'id',
            render: (value, item) => `
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-sm btn-outline-primary" 
                            onclick="editRegistro(${value})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger" 
                            onclick="deleteRegistro(${value})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `
        }
    ];

    // Crear tabla básica
    const table = initializeDataTable(selector);

    // Crear encabezados si no existen
    const thead = table.element.querySelector('thead');
    if (!thead) {
        const newThead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        const headers = ['ID', 'Sitio', 'Usuario', 'Estado', 'Fecha Creación', 'Acciones'];
        headers.forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            headerRow.appendChild(th);
        });
        
        newThead.appendChild(headerRow);
        table.element.appendChild(newThead);
    }

    // Cargar datos directamente
    loadTableData(table, data, columns);

    return table;
}

// Exportar funciones para uso global
window.DataTableUtils = {
    initializeDataTable,
    loadTableData,
    updateTableFromAPI,
    createRegistrosTable
};
