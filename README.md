# Emysic — Panel de Administración

Panel de administración desarrollado con **Flask + Bootstrap 5 + MySQL**.  
Tema visual inspirado en **YouTube Music** (modo oscuro).

🌐 **Demo en línea:** [Suemy.pythonanywhere.com](https://Suemy.pythonanywhere.com)  
📁 **Repositorio:** [github.com/EMY2882/Emysic](https://github.com/EMY2882/Emysic)

---

## Estructura del proyecto

```
emysic/
├── app.py                  ← Aplicación Flask principal + rutas + decoradores de roles
├── session_manager.py      ← Manejo de tokens de sesión (crear, verificar, renovar, cerrar)
├── requirements.txt        ← Dependencias pip
├── emysic_db.sql           ← Script MySQL completo
│
├── static/
│   ├── css/
│   │   └── estilos.css     ← Todos los estilos (tema YouTube Music oscuro)
│   ├── js/
│   │   └── funciones.js    ← Token watcher, verificación automática, helpers
│   └── img/                ← Recursos de imagen
│
└── templates/
    ├── landing.html            ← Página pública de inicio
    ├── layout.html             ← Plantilla base (sidebar + topbar + modal sesión)
    ├── login.html              ← Página de inicio de sesión
    ├── dashboard.html          ← Panel principal con estadísticas
    ├── acceso_denegado.html    ← Página 403 para roles sin permiso
    ├── usuarios/
    │   ├── index.html          ← Lista de usuarios
    │   └── form.html           ← Alta / edición de usuario
    ├── artistas/
    │   ├── index.html          ← Lista de artistas + preview iTunes
    │   └── form.html           ← Alta / edición de artista
    ├── generos/
    │   ├── index.html          ← Lista de géneros musicales
    │   └── form.html           ← Alta / edición de género
    ├── canciones/
    │   ├── index.html          ← Lista de canciones + preview iTunes
    │   └── form.html           ← Alta / edición de canción
    └── config/
        ├── index.html          ← Lista de parámetros del sistema
        └── form.html           ← Edición de parámetro
```

---

## Instalación local (VS Code + Terminal)

### 1. Base de datos MySQL

```bash
mysql -u root < emysic_db.sql
```

### 2. Entorno virtual

```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS / Linux
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar MySQL en `app.py`

```python
app.config['MYSQL_PASSWORD'] = 'tu_contraseña'
```

### 5. Ejecutar

```bash
python app.py
```

Abrir en: **http://127.0.0.1:3000**

---

## Credenciales por defecto

| Campo | Valor |
|---|---|
| Usuario | `emy` |
| Contraseña | `Admin1234!` |

---

## Funcionalidades

| Requisito | Implementación |
|---|---|
| Landing page pública | `landing.html` con tema YouTube Music |
| Login con Bootstrap | `login.html` — validación contra BD |
| Tokens de sesión únicos | `session_manager.py` — MD5 + tabla `token` |
| Tiempo del token parametrizado | `config_sistema.TOKEN_MINUTOS` editable desde UI |
| Verificación automática cada 5 min | `setInterval(verificarSesion, 300000)` en `funciones.js` |
| Modal de aviso 30 seg antes | Modal en `layout.html` con cuenta regresiva |
| Renovación manual del token | Clic en pill `▶ 00:00` en topbar |
| Dashboard con estadísticas | Conteos de usuarios, artistas, géneros y canciones |
| Catálogo 1 — Usuarios | Alta / Baja / Cambio con roles |
| Catálogo 2 — Artistas | Alta / Baja / Cambio + preview iTunes API |
| Catálogo 3 — Géneros | Alta / Baja / Cambio |
| Catálogo 4 — Canciones | Alta / Baja / Cambio + preview iTunes API |
| Configuración del sistema | Parámetros editables desde UI |
| Roles y permisos | Admin / Editor / Viewer con restricciones |
| Preview de audio | iTunes API — 30 segundos legal y gratuito |
| Deploy en la nube | PythonAnywhere (plan de paga) |
| BD en la nube | MySQL en PythonAnywhere |

---

## Sistema de roles

| Acción | Admin | Editor | Viewer |
|---|---|---|---|
| Ver todos los catálogos | ✅ | ✅ | ✅ |
| Crear / Editar artistas, géneros, canciones | ✅ | ✅ | ❌ |
| Eliminar registros | ✅ | ❌ | ❌ |
| Gestionar usuarios | ✅ | ❌ | ❌ |
| Editar configuración del sistema | ✅ | ❌ | ❌ |

---

## Flujo del token de sesión

```
Login → token creado en tabla `token` con dFecha = NOW() + TOKEN_MINUTOS
         │
         ├─► Cookie de sesión Flask (c_valor = MD5)
         │
         └─► Cada 5 minutos: GET /sesion-estado
                  ├─ ok=true  → actualiza contador en topbar
                  └─ ok=false → redirige a /login?expirado=1

30 segundos antes de expirar:
         └─► Modal "¿Sigues activo?" con cuenta regresiva

Clic en pill o botón "Continuar":
         └─► POST /renovar-sesion → dFecha = NOW() + TOKEN_MINUTOS
```

---

## Deploy en PythonAnywhere

```bash
# Clonar desde GitHub
cd ~
git clone https://github.com/EMY2882/Emysic.git

# Instalar dependencias
cd Emysic
pip install -r requirements.txt --user

# Actualizar cambios
git pull origin main
```

Configuración MySQL en PythonAnywhere:
```python
app.config['MYSQL_HOST']     = 'Suemy.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER']     = 'Suemy'
app.config['MYSQL_PASSWORD'] = 'tu_contraseña_pythonanywhere'
app.config['MYSQL_DB']       = 'Suemy$emysic_db'
```

---

## Tecnologías utilizadas

- **Backend:** Python 3.13 + Flask 3.0
- **Base de datos:** MySQL 8 (local y PythonAnywhere)
- **Frontend:** Bootstrap 5.3 + Bootstrap Icons
- **Fuentes:** DM Sans + Bebas Neue (Google Fonts)
- **API externa:** iTunes Search API (previews de audio)
- **Control de versiones:** Git + GitHub
- **Hosting:** PythonAnywhere (plan Revelador $10/mes)

---

*Proyecto Escolar — Tecnologías Web — Universidad Privada de la Península (UPP)*
