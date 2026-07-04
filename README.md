# Emysic — Panel de Administración

Panel de administración desarrollado con **Flask + Bootstrap 5 + MySQL**.
Tema visual: **YouTube Music** (modo oscuro).

## Estructura del proyecto

```
emysic/
├── app.py                  ← Aplicación Flask principal
├── session_manager.py      ← Manejo de tokens de sesión
├── requirements.txt        ← Dependencias pip
├── emysic_db.sql           ← Script MySQL completo
│
├── static/
│   ├── css/
│   │   └── estilos.css     ← Todos los estilos (tema YouTube Music)
│   ├── js/
│   │   └── funciones.js    ← Lógica JS: token watcher, helpers
│   └── img/                ← Imágenes (disponible para recursos)
│
└── templates/
    ├── layout.html         ← Plantilla base (sidebar + topbar + modal sesión)
    ├── login.html          ← Página de inicio de sesión (standalone)
    ├── dashboard.html      ← Panel principal con estadísticas
    ├── usuarios/
    │   ├── index.html      ← Lista de usuarios
    │   └── form.html       ← Alta / edición de usuario
    ├── artistas/
    │   ├── index.html      ← Lista de artistas
    │   └── form.html       ← Alta / edición de artista
    └── config/
        ├── index.html      ← Lista de parámetros del sistema
        └── form.html       ← Edición de parámetro
```

## Instalación (Visual Studio Code + Terminal local)

### 1. Base de datos MySQL

Abre MySQL Workbench o terminal y ejecuta:

```bash
mysql -u root -p < emysic_db.sql
```

### 2. Abrir en VS Code

```
Archivo → Abrir carpeta → seleccionar emysic/
```

### 3. Entorno virtual (terminal integrada: Ctrl + `)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar contraseña MySQL

Edita `app.py` línea ~15:

```python
app.config['MYSQL_PASSWORD'] = 'tu_contraseña_aqui'
```

### 6. Ejecutar

```bash
python app.py
```

Abre en el navegador: **http://127.0.0.1:3000**

## Credenciales por defecto

| Campo    | Valor       |
|----------|-------------|
| Usuario  | `emy`     |
| Password | `Admin1234!`|

> **Nota:** Si el hash de contraseña no coincide, ejecuta en Python:
> ```python
> from werkzeug.security import generate_password_hash
> print(generate_password_hash("Admin1234!"))
> ```
> Y actualiza el campo `password` en la tabla `usuario`.

## Funcionalidades

| Requisito | Implementación |
|-----------|----------------|
| Login Bootstrap | `login.html` tema YouTube Music oscuro |
| Dashboard | Estadísticas + accesos rápidos |
| Catálogo 1 — Usuarios | Alta / Baja / Cambio completo |
| Catálogo 2 — Artistas | Alta / Baja / Cambio completo |
| Renovación manual de token | Clic en pill `▶ 00:00` en topbar |
| Verificación automática cada 2 min | `setInterval(verificarSesion, 120000)` en `funciones.js` |
| Modal de aviso (30 seg antes) | Modal en `layout.html` + `funciones.js` |
| Tiempo del token parametrizado | `config_sistema.TOKEN_MINUTOS` editable desde UI |

## Flujo del token de sesión

```
Login → se crea registro en tabla `token` con dFecha = NOW() + TOKEN_MINUTOS
         │
         ├─► Cookie de sesión Flask (c_valor = MD5 del token)
         │
         └─► Cada 2 minutos: GET /sesion-estado
                  ├─ ok=true  → actualiza contador en topbar
                  └─ ok=false → redirige a /login?expirado=1

30 segundos antes de expirar:
         └─► Modal "¿Sigues activo?" con cuenta regresiva

Clic en pill / botón "Continuar":
         └─► POST /renovar-sesion → dFecha = NOW() + TOKEN_MINUTOS
```

## Parámetros configurables desde la UI

| Clave | Default | Descripción |
|-------|---------|-------------|
| `TOKEN_MINUTOS` | `30` | Tiempo de sesión en minutos |
| `APP_NOMBRE` | `Emysic` | Nombre de la app |
| `MAX_INTENTOS` | `5` | Intentos máximos de login |
