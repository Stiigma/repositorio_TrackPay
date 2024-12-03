document.addEventListener('DOMContentLoaded', () => {
    // Variables globales
    const addModal = document.getElementById('add-modal');
    const payUnitForm = document.getElementById('payUnitForm');
    const payReqForm = document.getElementById('payReqForm');
    const listaPagos = document.getElementById('lista-pagos');
    const editModal = document.getElementById('edit-subscription-modal');
    const saveChangesBtn = document.getElementById('save-changes-btn');
    const nameInput = document.getElementById('subscription-name');
    const dateInput = document.getElementById('subscription-date');
    const temporalityInput = document.getElementById('subscription-temporality');
    const typeInput = document.getElementById('subscription-type');
    const amountInput = document.getElementById('subscription-amount');
    const configUser = document.getElementById('config-modal')


    payUnitForm.style.display = 'none';

    let currentPagoId = null; 
    let currentPagoClase = null; 

    
    const showModal = (modal) => {
        modal.style.display = 'flex';
    };

    
    const closeModal = (modal) => {
        modal.style.display = 'none';
    };

    // Función "Modificar"
    const initializeEditButtons = () => {
        document.querySelectorAll('.edit-btn').forEach((button) => {
            button.addEventListener('click', () => {
                const pagoId = button.getAttribute('data-id');
                const pagoClase = button.closest('.pago-item').getAttribute('data-clase');
                currentPagoId = pagoId; 
                currentPagoClase = pagoClase; 

                
                nameInput.value = '';
                dateInput.value = '';
                temporalityInput.value = 'mensual';
                typeInput.value = 'entretenimiento';
                amountInput.value = '';

                
                showModal(editModal);
            });
        });

        document.getElementById('close-edit-modal').addEventListener('click', () => closeModal(editModal));
    };

    const initializeConfigButtons = () => {
        document.getElementById('config-btn').addEventListener('click', () => showModal(configUser));
        document.getElementById('close-config-modal').addEventListener('click', () => closeModal(configUser));
    }

    // Función modal de edición
    const saveChanges = async () => {
        if (!currentPagoId || !currentPagoClase) {
            alert('No se pudo identificar el pago a modificar.');
            return;
        }

        
        const data = {
            tipo_clase: currentPagoClase,
            'subscription-name': nameInput.value,
            'subscription-date': dateInput.value,
            'subscription-temporality': temporalityInput.value,
            'subscription-type': typeInput.value,
            'subscription-amount': amountInput.value,
        };

        try {
            const response = await fetch(`/editar_pago/${currentPagoId}/`, {
                method: 'POST',
                body: JSON.stringify(data),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            });

            const result = await response.json();

            if (result.success) {
                alert(result.message); 
                closeModal(editModal); 
                actualizarListaPagos(); 
            } else {
                alert(result.error || 'No se pudo guardar el pago.');
            }
        } catch (error) {
            console.error('Error al guardar cambios:', error);
            alert('Hubo un error al procesar la solicitud.');
        }
    };

    // Función para agregar un pago único o recurrente
    const submitForm = async (form, url) => {
        const formData = new FormData(form);

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            });

            const result = await response.json();

            if (result.success) {
                alert(result.message);
                closeModal(addModal); 
                actualizarListaPagos(); 
                form.reset(); 
            } 
            else 
            { 
                alert('Errores: ' + JSON.stringify(result.errors)); 
            } 
        } 
        catch (error) { 
            console.error('Error al enviar el formulario:', error); 
            alert('Hubo un error al procesar la solicitud.'); 
        } };

    // Función  "Eliminar"
    const initializeDeleteButtons = () => {
        document.querySelectorAll('.delete-btn').forEach((button) => {
            button.addEventListener('click', () => {
                const pagoId = button.getAttribute('data-id');
                if (confirm('¿Estás seguro de que deseas eliminar este pago?')) {
                    eliminarPago(pagoId);
                }
            });
        });
    };

    // Función para eliminar un pago
    const eliminarPago = async (pagoId) => {
        try {
            const response = await fetch(`/eliminar-pago/${pagoId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Token CSRF
                },
            });

            const data = await response.json();

            if (data.success) {
                alert('Pago eliminado exitosamente.');
                actualizarListaPagos(); 
            } else {
                alert(data.error || 'No se pudo eliminar el pago.');
            }
        } catch (error) {
            console.error('Error al eliminar el pago:', error);
            alert('Hubo un error al procesar la solicitud.');
        }
    };

    // Filtrado de pagos
    const filterSelect = document.getElementById("filter-select");

    filterSelect.addEventListener("change", () => {
        const filtro = filterSelect.value;
        const pagosItems = document.querySelectorAll("#lista-pagos .pago-item");
 
        pagosItems.forEach((item) => {
            const clase = item.getAttribute("data-clase");
 
            
            if (filtro === "todos") {
                item.style.display = "block";
            }
           
            else if (filtro === "pagos_unicos" && clase === "pago_unico") {
                item.style.display = "block";
            }
            
            else if (filtro === "pagos_recurrentes" && clase === "pago_recurrente") {
                item.style.display = "block";
            }
           
            else {
                item.style.display = "none";
            }
        });
    });

    // Función lista de pagos
    const actualizarListaPagos = async () => {
        try {
            const response = await fetch('/ruta-obtener-pagos/');
            const data = await response.json();

            listaPagos.innerHTML = ''; 
            if (data.length === 0) {
                listaPagos.innerHTML = '<div class="row"><div colspan="6">No hay pagos activos.</div></div>';
                return;
            }

            data.forEach((pago) => {
                const pagoHTML = `
                    <div class="pago-item" id="${pago.id}" data-clase="${pago.clase}">
                        <div class="row">
                            <div>${pago.concepto}</div>
                            <div>${pago.fecha || pago.fecha_fin}</div>
                            <div>${pago.frecuencia || 'Ninguna'}</div>
                            <div>${pago.tipo}</div>
                            <div>$${pago.monto}</div>
                            <div class="actions">
                                <button class="edit-btn" data-id="${pago.id}">Modificar</button>
                                <button class="delete-btn" data-id="${pago.id}">Eliminar</button>
                            </div>
                        </div>
                    </div>`;
                listaPagos.innerHTML += pagoHTML;
            });

            initializeEditButtons(); 
            initializeDeleteButtons(); 
        } catch (error) {
            console.error('Error al actualizar la lista de pagos:', error);
        }
    };

    // Inicializar eventos específicos
    const initializeAddModalEvents = () => {
        document.getElementById('add-btn').addEventListener('click', () => showModal(addModal));
        document.getElementById('close-add-modal').addEventListener('click', () => closeModal(addModal));
        document.getElementById('switch-to-recurrent').addEventListener('click', () => {
            payUnitForm.style.display = 'none';
            payReqForm.style.display = 'block';
        });
        document.getElementById('switch-to-unit').addEventListener('click', () => {
            payReqForm.style.display = 'none';
            payUnitForm.style.display = 'block';
        });

        payUnitForm.addEventListener('submit', (e) => {
            e.preventDefault();
            submitForm(payUnitForm, '/crear_pago_unico/');
        });

        
        payReqForm.addEventListener('submit', (e) => {
            e.preventDefault();
            submitForm(payReqForm, '/crear_pago_recurrente/');
        });

       
        window.addEventListener('click', (e) => {
            if (e.target === addModal) closeModal(addModal);
            if (e.target === editModal) closeModal(editModal);
            if (e.target === configUser) closeModal(configUser);
        });
    };

    // Inicializar eventos
    saveChangesBtn.addEventListener('click', saveChanges);
    initializeAddModalEvents();
    initializeConfigButtons();
    actualizarListaPagos();
});
