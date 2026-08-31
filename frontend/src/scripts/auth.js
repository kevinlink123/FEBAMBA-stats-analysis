// src/scripts/auth.js

// 🔑 Contraseña hasheada (generada con el script que te doy abajo)
// Esta es la contraseña "admin123" en SHA-256
const PASSWORD_HASH = '8ac29f02f847804afcda7b78de476291ce71a97a4398d188eabab65ff5ab2588';

/**
 * Genera un hash SHA-256 de un texto
 */
async function hashPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Verifica si la contraseña ingresada es correcta
 */
async function checkPassword(inputPassword) {
    const inputHash = await hashPassword(inputPassword);
    return inputHash === PASSWORD_HASH;
}

/**
 * Verifica si el usuario ya está autenticado
 */
function isAuthenticated() {
    const token = sessionStorage.getItem('auth_token');
    return token === PASSWORD_HASH;
}

/**
 * Muestra el diálogo de autenticación
 */
function showAuthDialog() {
    // Crear overlay
    const overlay = document.createElement('div');
    overlay.id = 'authOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(8px);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        font-family: 'Segoe UI', Roboto, system-ui, sans-serif;
        animation: fadeIn 0.3s ease-out;
    `;

    // Estilos de animación
    const styleSheet = document.createElement('style');
    styleSheet.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        #authDialog {
            animation: slideUp 0.3s ease-out;
        }
    `;
    document.head.appendChild(styleSheet);

    // Crear el diálogo
    overlay.innerHTML = `
        <div id="authDialog" style="
            background: white;
            padding: 2.5rem;
            border-radius: 24px;
            max-width: 420px;
            width: 90%;
            box-shadow: 0 24px 80px rgba(0,0,0,0.4);
            text-align: center;
        ">
            <div style="
                width: 64px;
                height: 64px;
                background: #1e1e1e;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1.5rem;
                font-size: 2rem;
            ">
                🔒
            </div>
            
            <h2 style="
                font-size: 1.5rem;
                font-weight: 300;
                color: #1e1e1e;
                margin-bottom: 0.5rem;
            ">
                <strong>Acceso</strong> restringido
            </h2>
            <p style="
                color: #777;
                font-size: 0.9rem;
                margin-bottom: 1.5rem;
            ">
                Ingresa la contraseña para acceder al contenido
            </p>
            
            <form id="authForm" style="display: flex; flex-direction: column; gap: 1rem;">
                <div style="position: relative;">
                    <input
                        type="password"
                        id="passwordInput"
                        placeholder="Contraseña..."
                        style="
                            width: 100%;
                            padding: 0.875rem 1rem;
                            border: 2px solid #d0d0d0;
                            border-radius: 14px;
                            font-size: 1rem;
                            outline: none;
                            transition: all 0.2s;
                            background: #fafafa;
                            box-sizing: border-box;
                        "
                        autofocus
                    />
                </div>
                
                <button
                    type="submit"
                    id="submitBtn"
                    style="
                        padding: 0.875rem;
                        background: #1e1e1e;
                        color: white;
                        border: none;
                        border-radius: 14px;
                        font-size: 1rem;
                        font-weight: 500;
                        cursor: pointer;
                        transition: all 0.2s;
                        position: relative;
                    "
                    onmouseover="this.style.background='#333'"
                    onmouseout="this.style.background='#1e1e1e'"
                >
                    <span id="submitText">Ingresar</span>
                    <span id="loadingSpinner" style="display: none;">
                        <svg class="animate-spin" style="width: 20px; height: 20px;" viewBox="0 0 24 24">
                            <circle style="opacity: 0.25;" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                            <path style="opacity: 0.75;" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                        </svg>
                    </span>
                </button>
            </form>
            
            <div id="authError" style="
                margin-top: 1rem;
                color: #dc2626;
                font-size: 0.875rem;
                display: none;
                background: #fef2f2;
                padding: 0.75rem;
                border-radius: 12px;
                border: 1px solid #fecaca;
            ">
                ❌ Contraseña incorrecta. Por favor, intenta nuevamente.
            </div>
            
            <div style="margin-top: 1.5rem; font-size: 0.75rem; color: #aaa;">
                Contacta al administrador si no tienes acceso
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    // Manejar el formulario
    const form = overlay.querySelector('#authForm');
    const passwordInput = overlay.querySelector('#passwordInput');
    const errorDiv = overlay.querySelector('#authError');
    const submitBtn = overlay.querySelector('#submitBtn');
    const submitText = overlay.querySelector('#submitText');
    const loadingSpinner = overlay.querySelector('#loadingSpinner');

    // Manejar error de entrada
    passwordInput.addEventListener('input', () => {
        passwordInput.style.borderColor = '#d0d0d0';
        errorDiv.style.display = 'none';
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const password = passwordInput.value.trim();
        
        if (!password) {
            passwordInput.style.borderColor = '#dc2626';
            errorDiv.textContent = '⚠️ Por favor, ingresa la contraseña';
            errorDiv.style.display = 'block';
            return;
        }

        // Mostrar loading
        submitBtn.disabled = true;
        submitText.style.display = 'none';
        loadingSpinner.style.display = 'inline-block';
        errorDiv.style.display = 'none';

        try {
            const isValid = await checkPassword(password);
            
            if (isValid) {
                // ✅ Autenticación exitosa
                sessionStorage.setItem('auth_token', PASSWORD_HASH);
                
                // Animar salida
                const dialog = overlay.querySelector('#authDialog');
                dialog.style.animation = 'slideUp 0.2s ease-out reverse';
                
                setTimeout(() => {
                    overlay.remove();
                    // Mostrar el contenido
                    document.body.style.display = '';
                    // Recargar para asegurar que todo funcione
                    window.location.reload();
                }, 200);
            } else {
                // ❌ Error
                errorDiv.style.display = 'block';
                passwordInput.style.borderColor = '#dc2626';
                passwordInput.value = '';
                passwordInput.focus();
                
                // Resetear botón
                submitBtn.disabled = false;
                submitText.style.display = 'inline';
                loadingSpinner.style.display = 'none';
                
                // Limpiar error después de 4 segundos
                setTimeout(() => {
                    errorDiv.style.display = 'none';
                    passwordInput.style.borderColor = '#d0d0d0';
                }, 4000);
            }
        } catch (error) {
            console.error('Error de autenticación:', error);
            errorDiv.textContent = '❌ Error al verificar la contraseña';
            errorDiv.style.display = 'block';
            submitBtn.disabled = false;
            submitText.style.display = 'inline';
            loadingSpinner.style.display = 'none';
        }
    });

    // Enfoque automático
    setTimeout(() => passwordInput.focus(), 300);

    // Manejar tecla Escape para cancelar (opcional)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && document.getElementById('authOverlay')) {
            // No permitir cerrar el diálogo
            e.preventDefault();
        }
    });
}

/**
 * Inicializar la autenticación
 */
document.addEventListener('DOMContentLoaded', () => {
    // Ocultar contenido inicialmente
    // document.body.style.display = 'none';
    
    if (!isAuthenticated()) {
        showAuthDialog();
    } else {
        document.body.style.display = '';
    }
});

// ✅ Función para cerrar sesión (opcional)
window.logout = function() {
    sessionStorage.removeItem('auth_token');
    window.location.reload();
};