document.addEventListener('DOMContentLoaded', () => {
    // Modales
    const addModal = document.getElementById('add-modal');
    const configModal = document.getElementById('config-modal');
    const editSubscriptionModal = document.getElementById('edit-subscription-modal');

    // Formularios
    const payUnitForm = document.getElementById('payUnitForm');
    const payReqForm = document.getElementById('payReqForm');

    // Botones
    const addBtn = document.getElementById('add-btn');
    const closeAddModal = document.getElementById('close-add-modal');
    const switchToRecurrent = document.getElementById('switch-to-recurrent');
    const switchToUnit = document.getElementById('switch-to-unit');
    const configBtn = document.getElementById('config-btn');
    const closeConfigModal = document.getElementById('close-config-modal');
    const closeEditModal = document.getElementById('close-edit-modal');
    const saveChangesBtn = document.getElementById('save-changes-btn');

    // Inputs del modal de edición
    const nameInput = document.getElementById('subscription-name');
    const dateInput = document.getElementById('subscription-date');
    const temporalityInput = document.getElementById('subscription-temporality');
    const typeInput = document.getElementById('subscription-type');
    const amountInput = document.getElementById('subscription-amount');

    // Mostrar por defecto el formulario de Pago Único
    payReqForm.style.display = 'none';
    payUnitForm.style.display = 'block';

    // Abrir y cerrar el modal "Nuevo Pago"
    addBtn.addEventListener('click', () => {
        addModal.style.display = 'flex';
    });

    closeAddModal.addEventListener('click', () => {
        addModal.style.display = 'none';
    });

    // Alternar entre formularios
    switchToRecurrent.addEventListener('click', () => {
        payUnitForm.style.display = 'none';
        payReqForm.style.display = 'block';
    });

    switchToUnit.addEventListener('click', () => {
        payReqForm.style.display = 'none';
        payUnitForm.style.display = 'block';
    });

    // Abrir y cerrar el modal "Configuración"
    configBtn.addEventListener('click', () => {
        configModal.style.display = 'flex';
    });

    closeConfigModal.addEventListener('click', () => {
        configModal.style.display = 'none';
    });

    // Cerrar modales si se hace clic fuera
    window.addEventListener('click', (e) => {
        if (e.target === addModal) addModal.style.display = 'none';
        if (e.target === configModal) configModal.style.display = 'none';
        if (e.target === editSubscriptionModal) editSubscriptionModal.style.display = 'none';
    });

    // Enviar formulario para crear Pago Único
    payUnitForm.addEventListener('submit', (e) => {
        e.preventDefault();
        submitForm(payUnitForm, '/crear_pago_unico/');
    });

    // Enviar formulario para crear Pago Recurrente
    payReqForm.addEventListener('submit', (e) => {
        e.preventDefault();
        submitForm(payReqForm, '/crear_pago_recurrente/');
    });

    // Función para enviar formularios
    async function submitForm(form, url) {
        const formData = new FormData(form);

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            });

            const data = await response.json();
            if (data.success) {
                alert('Pago guardado exitosamente.');
                form.reset();
                addModal.style.display = 'none';
                actualizarPagos();
            } else {
                alert('Error: ' + JSON.stringify(data.errors));
            }
        } catch (error) {
            console.error('Error al enviar el formulario:', error);
        }
    }

    // Función para actualizar la lista de pagos
    function actualizarPagos() {
        fetch('/ruta-obtener-pagos/')
            .then(response => response.json())
            .then(data => {
                const contenedorPagos = document.getElementById('lista-pagos');
                contenedorPagos.innerHTML = '';

                if (data.length === 0) {
                    contenedorPagos.innerHTML = '<div class="row"><div colspan="6">No hay pagos activos.</div></div>';
                    return;
                }

                data.forEach(pago => {
                    const pagoHTML = `
                        <div class="row" data-id="${pago.id}" data-clase="${pago.clase}">
                            <div>${pago.concepto}</div>
                            <div>${pago.fecha || pago.fecha_fin}</div>
                            <div>${pago.frecuencia || "Ninguna"}</div>
                            <div>${pago.tipo}</div>
                            <div>$${pago.monto}</div>
                            <div class="actions">
                                <button class="edit-btn" data-id="${pago.id}" data-clase="${pago.clase}">Modificar</button>
                                <button class="delete-btn" data-id="${pago.id}">Eliminar</button>
                            </div>
                        </div>`;
                    contenedorPagos.innerHTML += pagoHTML;
                });
            })
            .catch(error => console.error('Error al obtener pagos:', error));
    }

    // Función para manejar eliminación de pagos
    function borrarPago() {
        const listaPagos = document.getElementById('lista-pagos');
        listaPagos.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-btn')) {
                const pagoId = e.target.getAttribute('data-id');
                if (confirm("¿Estás seguro de que deseas eliminar este pago?")) {
                    eliminarPagoBackend(pagoId);
                }
            }
        });
    }

    // Función para eliminar un pago en el backend
    function eliminarPagoBackend(pagoId) {
        fetch(`/eliminar-pago/${pagoId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Pago eliminado correctamente.');
                    actualizarPagos();
                } else {
                    alert('Error al eliminar el pago: ' + data.error);
                }
            })
            .catch(error => console.error('Error al eliminar el pago:', error));
    }

    function abrirModalEdicion(row, pagoId, tipoClase) {
        editSubscriptionModal.setAttribute('data-id', pagoId);
        editSubscriptionModal.setAttribute('data-clase', tipoClase); // Asigna la clase al modal
        console.log("ID del pago asignado al modal:", pagoId);
        console.log("Clase del pago asignada al modal:", tipoClase);
    
        const columns = row.querySelectorAll('div');
        nameInput.value = columns[0].textContent.trim();
        dateInput.value = new Date(columns[1].textContent.trim()).toISOString().split('T')[0];
        temporalityInput.value = columns[2].textContent.trim();
        typeInput.value = columns[3].textContent.trim();
        amountInput.value = parseFloat(columns[4].textContent.trim().replace('$', ''));
    
        editSubscriptionModal.style.display = 'flex';
    }
    
    // Delegar evento de clic para editar
    document.getElementById('lista-pagos').addEventListener('click', (e) => {
        if (e.target.classList.contains('edit-btn')) {
            const row = e.target.closest('.row');
            const pagoId = row.getAttribute('data-id');
            const tipoClase = row.getAttribute('data-clase');
            abrirModalEdicion(row, pagoId, tipoClase);
        }
    });

    // Función para modificar un pago en el backend
    function modificarPagoBackend(pagoId, updatedData) {
        fetch(`/editar_pago/${pagoId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedData),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Pago modificado correctamente.');
                    actualizarPagos();
                    editSubscriptionModal.style.display = 'none';
                } else {
                    alert('Error al modificar el pago: ' + data.error);
                }
            })
            .catch(error => console.error('Error al modificar el pago:', error));
    }
    
    
    // Guardar cambios en el backend
    saveChangesBtn.addEventListener('click', () => {
        const pagoId = editSubscriptionModal.getAttribute('data-id');
        const tipoClase = editSubscriptionModal.getAttribute('data-clase'); // Obtén el tipo de clase
    
        const updatedData = {
            'subscription-name': nameInput.value,
            'subscription-date': dateInput.value,
            'subscription-temporality': temporalityInput.value,
            'subscription-type': typeInput.value,
            'subscription-amount': amountInput.value,
            'tipo_clase': tipoClase // Enviar el tipo de clase al backend
        };
    
        if (pagoId && tipoClase) {
            modificarPagoBackend(pagoId, updatedData);
        } else {
            alert('Error: No se pudo obtener el ID o tipo de clase del pago.');
        }
    });

    // Inicializar funcionalidades
    borrarPago();
    actualizarPagos();
});
