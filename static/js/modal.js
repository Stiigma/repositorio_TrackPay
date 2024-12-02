document.addEventListener('DOMContentLoaded', () => {
    // Modal de "Nuevo Pago" y sus botones
    const addModal = document.getElementById('add-modal');
    const closeAddModal = document.getElementById('close-add-modal');
    const payUnitForm = document.getElementById('payUnitForm');
    const payReqForm = document.getElementById('payReqForm');
    const switchToRecurrent = document.getElementById('switch-to-recurrent');
    const switchToUnit = document.getElementById('switch-to-unit');
    const addBtn = document.getElementById('add-btn');

    // Modal de "Configuración" y sus botones
    const configModal = document.getElementById('config-modal');
    const closeConfigModal = document.getElementById('close-config-modal');
    const configBtn = document.getElementById('config-btn');

    // Mostrar por defecto solo el formulario de Pago Único
    payReqForm.style.display = 'none';
    payUnitForm.style.display = 'block';

    // Abrir y cerrar el modal "Nuevo Pago"
    addBtn.addEventListener('click', () => {
        addModal.style.display = 'flex';
    });

    closeAddModal.addEventListener('click', () => {
        addModal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === addModal) {
            addModal.style.display = 'none';
        }
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

    window.addEventListener('click', (e) => {
        if (e.target === configModal) {
            configModal.style.display = 'none';
        }
    });

    // Enviar Formulario de Pago Único
    payUnitForm.addEventListener('submit', (e) => {
        e.preventDefault();
        submitForm(payUnitForm, '/crear_pago_unico/');
    });

    // Enviar Formulario de Pago Recurrente
    payReqForm.addEventListener('submit', (e) => {
        e.preventDefault();
        submitForm(payReqForm, '/crear_pago_recurrente/');
    });

    // Función para enviar el formulario
    async function submitForm(form, url) {
        const formData = new FormData(form);

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Token CSRF
                },
            });

            const data = await response.json();
            if (data.success) {
                alert('Pago guardado exitosamente.');
                form.reset(); // Limpiar el formulario
                addModal.style.display = 'none'; // Cerrar el modal
                actualizarPagos(); // Actualizar la lista de pagos
            } else {
                alert('Error: ' + JSON.stringify(data.errors));
            }
        } catch (error) {
            console.error('Error al enviar el formulario:', error);
            alert('Hubo un error al enviar el formulario. Inténtalo de nuevo.');
        }
    }

    // Función para actualizar la lista de pagos
    function actualizarPagos() {
        fetch('/ruta-obtener-pagos/')  // Ajusta la URL según tu configuración
            .then(response => response.json())
            .then(data => {
                const contenedorPagos = document.getElementById('lista-pagos');
                contenedorPagos.innerHTML = ''; // Limpiar lista actual

                if (data.length === 0) {
                    // Mostrar mensaje si no hay pagos
                    contenedorPagos.innerHTML = `
                        <div class="row">
                            <div colspan="6">No hay pagos activos.</div>
                        </div>`;
                    return;
                }

                data.forEach(pago => {
                    // Determinar si es pago único o recurrente
                    const fecha = pago.clase === "pago_unico" ? pago.fecha : pago.fecha_fin;
                    const frecuencia = pago.clase === "pago_recurrente" ? pago.frecuencia : "Ninguna";

                    // Crear el HTML del pago
                    const pagoHTML = `
                        <div class="row">
                            <div>${pago.concepto}</div>
                            <div>${fecha}</div>
                            <div>${frecuencia}</div>
                            <div>${pago.tipo}</div>
                            <div>$${pago.monto}</div>
                            <div class="actions">
                                <button class="edit-btn">Modificar</button>
                                <button class="delete-btn" data-id="${pago.id}">Eliminar</button>
                            </div>
                        </div>`;

                    contenedorPagos.innerHTML += pagoHTML;
                });
            })
            .catch(error => console.error('Error al obtener pagos:', error));
    }

    // Inicializar eventos para eliminar pagos
    function borrarPago() {
        const listaPagos = document.getElementById('lista-pagos');

        listaPagos.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-btn')) {
                const pagoId = e.target.getAttribute('data-id');
                const confirmacion = confirm("¿Estás seguro de que deseas eliminar este pago?");
                if (confirmacion) {
                    eliminarPagoBackend(pagoId);
                }
            }
        });
    }

    // Función para eliminar el pago del backend
    function eliminarPagoBackend(pagoId) {
        fetch(`/eliminar-pago/${pagoId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Token CSRF
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Pago eliminado correctamente.');
                    actualizarPagos(); // Actualizar la lista después de eliminar
                } else {
                    alert('Error al eliminar el pago: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error al eliminar el pago:', error);
                alert('Hubo un error al intentar eliminar el pago. Inténtalo de nuevo.');
            });
    }

    borrarPago(); // Inicializar eventos de eliminación
});
