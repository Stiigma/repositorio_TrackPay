document.addEventListener('DOMContentLoaded', () => {
    const configUser = document.getElementById('config-modal');
    const configBtn = document.getElementById('config-btn');
    const closeConfigBtn = document.getElementById('close-config-modal');

    if (!configUser || !configBtn || !closeConfigBtn) {
        console.error('Error: Elementos del modal no encontrados.');
        return;
    }

    const showModal = () => {
        configUser.style.display = 'grid';
    };

    const closeModal = () => {
        configUser.style.display = 'none';
    };

    configBtn.addEventListener('click', showModal);
    closeConfigBtn.addEventListener('click', closeModal);

    // Opcional: Cerrar el modal al hacer clic fuera del contenido
    window.addEventListener('click', (e) => {
        if (e.target === configUser) {
            closeModal();
        }
    });
});