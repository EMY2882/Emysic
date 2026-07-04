/* ═══════════════════════════════════════════
   Emysic — funciones.js
   Funciones globales del panel de administración
═══════════════════════════════════════════ */

// ── Constante: segundos antes de mostrar aviso ────────────
const SEGUNDOS_AVISO = 60;

// ── Variables de estado ───────────────────────────────────
let modalMostrado   = false;
let cuentaRegresiva = null;
let watcherInterval = null;

// ── Mostrar / ocultar contraseña ──────────────────────────
function togglePw(inputId, iconId) {
    const pw   = document.getElementById(inputId || 'password');
    const icon = document.getElementById(iconId  || 'toggle-pw');
    if (!pw) return;
    if (pw.type === 'password') {
        pw.type = 'text';
        if (icon) icon.classList.replace('bi-eye', 'bi-eye-slash');
    } else {
        pw.type = 'password';
        if (icon) icon.classList.replace('bi-eye-slash', 'bi-eye');
    }
}

// ── Confirmación antes de eliminar ────────────────────────
function confirmarEliminar(formId, nombre) {
    if (confirm('¿Desactivar "' + nombre + '"?\nEsta acción se puede revertir editando el registro.')) {
        document.getElementById(formId).submit();
    }
}

// ── Búsqueda en tabla ─────────────────────────────────────
function filtrarTabla(inputId, tableId) {
    const filtro = document.getElementById(inputId).value.toLowerCase();
    const filas  = document.querySelectorAll('#' + tableId + ' tbody tr');
    filas.forEach(function(fila) {
        fila.style.display = fila.textContent.toLowerCase().includes(filtro) ? '' : 'none';
    });
}

// ── Token pill: actualizar visualización ──────────────────
function actualizarPill(segundos) {
    const pill  = document.getElementById('token-pill');
    const texto = document.getElementById('token-tiempo');
    if (!pill || !texto) return;

    const m  = Math.floor(Math.abs(segundos) / 60);
    const s  = Math.abs(segundos) % 60;
    texto.textContent = String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');

    pill.classList.remove('expiring', 'expired');
    if (segundos <= 0)              pill.classList.add('expired');
    else if (segundos <= SEGUNDOS_AVISO) pill.classList.add('expiring');
}

// ── Cuenta regresiva local (cada segundo) ─────────────────
let _segundosLocales = 0;
function iniciarContadorLocal(segundos) {
    _segundosLocales = segundos;
    actualizarPill(_segundosLocales);
    if (cuentaRegresiva) clearInterval(cuentaRegresiva);
    cuentaRegresiva = setInterval(function() {
        _segundosLocales--;
        actualizarPill(_segundosLocales);
        if (_segundosLocales <= SEGUNDOS_AVISO && !modalMostrado) {
            mostrarModalSesion(_segundosLocales);
        }
        if (_segundosLocales <= 0) {
            clearInterval(cuentaRegresiva);
        }
    }, 1000);
}

// ── Modal de sesión por expirar ───────────────────────────
function mostrarModalSesion(segundos) {
    const modal = document.getElementById('modal-sesion');
    if (!modal || modalMostrado) return;
    modalMostrado = true;
    modal.style.display = 'flex';
    iniciarCuentaRegresiva(segundos);
}

function iniciarCuentaRegresiva(segundos) {
    const span = document.getElementById('cuenta-regresiva');
    if (!span) return;
    span.textContent = segundos;
    let timer = setInterval(function() {
        segundos--;
        span.textContent = segundos;
        if (segundos <= 0) {
            clearInterval(timer);
            window.location.href = '/login?expirado=1';
        }
    }, 1000);
}

function continuarSesion() {
    fetch('/renovar-sesion', { method: 'POST' })
        .then(r => r.json())
        .then(function(data) {
            if (data.ok) {
                const modal = document.getElementById('modal-sesion');
                if (modal) modal.style.display = 'none';
                modalMostrado = false;
                // Re-sincronizar con servidor
                verificarSesion();
            } else {
                window.location.href = '/login?expirado=1';
            }
        })
        .catch(function() {
            window.location.href = '/login?expirado=1';
        });
}

// ── Verificar sesión en servidor (cada 2 minutos) ─────────
function verificarSesion() {
    fetch('/sesion-estado')
        .then(r => r.json())
        .then(function(data) {
            if (!data.ok) {
                window.location.href = '/login?expirado=1';
                return;
            }
            iniciarContadorLocal(data.segundos);
        })
        .catch(function() {
            // Sin conexión: no redirigir, seguir con contador local
        });
}

// ── Renovación manual (clic en pill) ─────────────────────
function renovarManual() {
    fetch('/renovar-sesion', { method: 'POST' })
        .then(r => r.json())
        .then(function(data) {
            if (data.ok) {
                verificarSesion();    // re-sincronizar
                mostrarToast('Sesión renovada correctamente.', 'success');
            }
        });
}

// ── Toast helper ─────────────────────────────────────────
function mostrarToast(mensaje, tipo) {
    tipo = tipo || 'success';
    const colores = {
        success: { bg: '#22c55e22', borde: '#22c55e44', texto: '#22c55e' },
        danger:  { bg: '#ef444422', borde: '#ef444444', texto: '#ef4444' },
        warning: { bg: '#f59e0b22', borde: '#f59e0b44', texto: '#f59e0b' },
    };
    const c = colores[tipo] || colores.success;
    const t = document.createElement('div');
    t.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:99999;' +
        'min-width:240px;padding:.75rem 1.1rem;border-radius:10px;' +
        'background:' + c.bg + ';border:1px solid ' + c.borde + ';' +
        'color:' + c.texto + ';font-size:.88rem;font-weight:600;' +
        'box-shadow:0 4px 16px rgba(0,0,0,.4);';
    t.textContent = mensaje;
    document.body.appendChild(t);
    setTimeout(function() { t.remove(); }, 2500);
}

// ── Auto-cerrar alertas Flash ─────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });

    // Iniciar watcher de sesión si estamos logueados
    const pill = document.getElementById('token-pill');
    if (pill) {
        verificarSesion();                           // inmediato
        watcherInterval = setInterval(verificarSesion, 120000); // cada 2 minutos
    }
});
