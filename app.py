# ============================================================
#  Emysic — app.py
#  Panel de administración tema YouTube Music
# ============================================================
import functools
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from session_manager import crear_sesion, verificar_token, renovar_token, cerrar_sesion

app = Flask(__name__)
app.secret_key = "emysic_sm_2026"

# ── MySQL ────────────────────────────────────────────────────
app.config['MYSQL_HOST']     = 'Suemy.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER']     = 'Suemy'
app.config['MYSQL_PASSWORD'] = 'Emysic282026!'
app.config['MYSQL_DB']       = 'Suemy$emysic_db'
app.config['MYSQL_PORT']     = 3306

mysql = MySQL(app)


# ── Decoradores ──────────────────────────────────────────────
def requiere_sesion(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        c_valor = session.get("c_valor")
        if not c_valor:
            return redirect(url_for('login'))
        sesion = verificar_token(mysql, c_valor)
        if not sesion:
            session.clear()
            return redirect(url_for('login') + "?expirado=1")
        return f(*args, **kwargs)
    return wrapper


def solo_admin(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("rol") != "admin":
            return render_template('acceso_denegado.html'), 403
        return f(*args, **kwargs)
    return wrapper


def admin_o_editor(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("rol") not in ["admin", "editor"]:
            return render_template('acceso_denegado.html'), 403
        return f(*args, **kwargs)
    return wrapper


# ── Rutas públicas ───────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('landing'))


@app.route('/landing')
def landing():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    expirado = request.args.get('expirado')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id, password, rol FROM usuario WHERE username = %s AND lActivo = 1",
            (username,)
        )
        usuario = cur.fetchone()
        cur.close()

        if usuario and check_password_hash(usuario[1], password):
            id_usuario = usuario[0]
            c_valor    = crear_sesion(mysql, id_usuario)
            session["c_valor"]    = c_valor
            session["id_usuario"] = id_usuario
            session["username"]   = username
            session["rol"]        = usuario[2]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos.")

    return render_template('login.html', expirado=expirado)


@app.route('/logout')
def logout():
    c_valor = session.get("c_valor")
    if c_valor:
        cerrar_sesion(mysql, c_valor)
    session.clear()
    return redirect(url_for('login'))


# ── Estado y renovación de sesión ───────────────────────────
@app.route('/sesion-estado')
def sesion_estado():
    c_valor = session.get("c_valor")
    if not c_valor:
        return {"ok": False, "segundos": 0}

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT TIMESTAMPDIFF(SECOND, NOW(), dFecha) FROM token WHERE cValor = %s AND lActivo = 1",
        (c_valor,)
    )
    row = cur.fetchone()
    cur.close()

    if not row or row[0] is None or row[0] <= 0:
        session.clear()
        return {"ok": False, "segundos": 0}

    return {"ok": True, "segundos": int(row[0])}


@app.route('/renovar-sesion', methods=['POST'])
def renovar_sesion_manual():
    c_valor = session.get("c_valor")
    if not c_valor:
        return {"ok": False}, 401
    renovado = renovar_token(mysql, c_valor)
    return {"ok": renovado}


# ── Dashboard ────────────────────────────────────────────────
@app.route('/dashboard')
@requiere_sesion
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM usuario WHERE lActivo = 1")
    total_usuarios = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM artista WHERE lActivo = 1")
    total_artistas = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM genero WHERE lActivo = 1")
    total_generos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM cancion WHERE lActivo = 1")
    total_canciones = cur.fetchone()[0]
    cur.execute("SELECT param_value FROM system_config WHERE param_key='TOKEN_LIFETIME_MINUTES'" if False else
                "SELECT valor FROM config_sistema WHERE clave = 'TOKEN_MINUTOS'")
    row = cur.fetchone()
    token_minutos = int(row[0]) if row else 30
    cur.close()

    return render_template('dashboard.html',
                           username=session.get('username', 'Admin'),
                           rol=session.get('rol', 'viewer'),
                           total_usuarios=total_usuarios,
                           total_artistas=total_artistas,
                           total_generos=total_generos,
                           total_canciones=total_canciones,
                           token_minutos=token_minutos)


# ── Catálogo: Usuarios ───────────────────────────────────────
@app.route('/usuarios')
@requiere_sesion
def usuarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, email, rol, lActivo, fecha_alta FROM usuario ORDER BY id")
    lista = cur.fetchall()
    cur.close()
    return render_template('usuarios/index.html', usuarios=lista)


@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@requiere_sesion
@solo_admin
def usuario_nuevo():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password'].strip()
        rol      = request.form.get('rol', 'viewer')
        pw_hash  = generate_password_hash(password)
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO usuario (username, email, password, rol) VALUES (%s,%s,%s,%s)",
                (username, email, pw_hash, rol)
            )
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            return render_template('usuarios/form.html', usuario=None, accion='Nuevo', error=str(e))
        return redirect(url_for('usuarios'))
    return render_template('usuarios/form.html', usuario=None, accion='Nuevo', error=None)


@app.route('/usuarios/editar/<int:uid>', methods=['GET', 'POST'])
@requiere_sesion
@solo_admin
def usuario_editar(uid):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        email    = request.form['email'].strip()
        rol      = request.form.get('rol', 'viewer')
        lActivo  = 1 if request.form.get('lActivo') else 0
        new_pass = request.form.get('password', '').strip()
        if new_pass:
            pw_hash = generate_password_hash(new_pass)
            username = request.form['username'].strip()
            cur.execute(
                "UPDATE usuario SET username=%s, email=%s, rol=%s, lActivo=%s WHERE id=%s",
                (username, email, rol, lActivo, uid)
            )
        else:
            cur.execute(
                "UPDATE usuario SET username=%s, email=%s, rol=%s, lActivo=%s, password=%s WHERE id=%s",
                (username, email, rol, lActivo, pw_hash, uid)
            )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('usuarios'))
    cur.execute("SELECT * FROM usuario WHERE id=%s", (uid,))
    usuario = cur.fetchone()
    cur.close()
    return render_template('usuarios/form.html', usuario=usuario, accion='Editar', error=None)


@app.route('/usuarios/eliminar/<int:uid>', methods=['POST'])
@requiere_sesion
@solo_admin
def usuario_eliminar(uid):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE usuario SET lActivo = 0 WHERE id = %s", (uid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('usuarios'))


# ── Catálogo: Artistas ───────────────────────────────────────
@app.route('/artistas')
@requiere_sesion
def artistas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre, genero, pais, lActivo FROM artista ORDER BY id")
    lista = cur.fetchall()
    cur.close()
    return render_template('artistas/index.html', artistas=lista)


@app.route('/artistas/nuevo', methods=['GET', 'POST'])
@requiere_sesion
@admin_o_editor
def artista_nuevo():
    if request.method == 'POST':
        nombre  = request.form['nombre'].strip()
        genero  = request.form.get('genero', '').strip()
        pais    = request.form.get('pais', '').strip()
        bio     = request.form.get('bio', '').strip()
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO artista (nombre, genero, pais, bio) VALUES (%s,%s,%s,%s)",
                (nombre, genero, pais, bio)
            )
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            return render_template('artistas/form.html', artista=None, accion='Crear', error=str(e))
        return redirect(url_for('artistas'))
    return render_template('artistas/form.html', artista=None, accion='Crear', error=None)


@app.route('/artistas/editar/<int:aid>', methods=['GET', 'POST'])
@requiere_sesion
@admin_o_editor
def artista_editar(aid):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nombre  = request.form['nombre'].strip()
        genero  = request.form.get('genero', '').strip()
        pais    = request.form.get('pais', '').strip()
        bio     = request.form.get('bio', '').strip()
        lActivo = 1 if request.form.get('lActivo') else 0
        cur.execute(
            "UPDATE artista SET nombre=%s, genero=%s, pais=%s, bio=%s, lActivo=%s WHERE id=%s",
            (nombre, genero, pais, bio, lActivo, aid)
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('artistas'))
    cur.execute("SELECT * FROM artista WHERE id=%s", (aid,))
    artista = cur.fetchone()
    cur.close()
    return render_template('artistas/form.html', artista=artista, accion='Editar', error=None)


@app.route('/artistas/eliminar/<int:aid>', methods=['POST'])
@requiere_sesion
@solo_admin
def artista_eliminar(aid):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE artista SET lActivo = 0 WHERE id = %s", (aid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('artistas'))


# ── Catálogo: Géneros ────────────────────────────────────────
@app.route('/generos')
@requiere_sesion
def generos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre, descripcion, lActivo, fecha_alta FROM genero ORDER BY nombre")
    lista = cur.fetchall()
    cur.close()
    return render_template('generos/index.html', generos=lista)


@app.route('/generos/nuevo', methods=['GET', 'POST'])
@requiere_sesion
@admin_o_editor
def genero_nuevo():
    if request.method == 'POST':
        nombre      = request.form['nombre'].strip()
        descripcion = request.form.get('descripcion', '').strip()
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO genero (nombre, descripcion) VALUES (%s,%s)", (nombre, descripcion))
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            return render_template('generos/form.html', genero=None, accion='Nuevo', error=str(e))
        return redirect(url_for('generos'))
    return render_template('generos/form.html', genero=None, accion='Nuevo', error=None)


@app.route('/generos/editar/<int:gid>', methods=['GET', 'POST'])
@requiere_sesion
@admin_o_editor
def genero_editar(gid):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nombre      = request.form['nombre'].strip()
        descripcion = request.form.get('descripcion', '').strip()
        lActivo     = 1 if request.form.get('lActivo') else 0
        cur.execute(
            "UPDATE genero SET nombre=%s, descripcion=%s, lActivo=%s WHERE id=%s",
            (nombre, descripcion, lActivo, gid)
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('generos'))
    cur.execute("SELECT * FROM genero WHERE id=%s", (gid,))
    genero = cur.fetchone()
    cur.close()
    return render_template('generos/form.html', genero=genero, accion='Editar', error=None)


@app.route('/generos/eliminar/<int:gid>', methods=['POST'])
@requiere_sesion
@solo_admin
def genero_eliminar(gid):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE genero SET lActivo = 0 WHERE id = %s", (gid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('generos'))


# ── Catálogo: Canciones ──────────────────────────────────────
@app.route('/canciones')
@requiere_sesion
def canciones():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.id, c.titulo, c.id_artista, c.id_genero, c.album, c.duracion,
               a.nombre AS artista, g.nombre AS genero, c.lActivo
        FROM cancion c
        JOIN artista a ON a.id = c.id_artista
        JOIN genero  g ON g.id = c.id_genero
        ORDER BY c.id
    """)
    lista = cur.fetchall()
    cur.close()
    return render_template('canciones/index.html', canciones=lista)


@app.route('/canciones/nueva', methods=['GET', 'POST'])
@requiere_sesion
@admin_o_editor
def cancion_nueva():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        titulo     = request.form['titulo'].strip()
        id_artista = request.form['id_artista']
        id_genero  = request.form['id_genero']
        album      = request.form.get('album', '').strip()
        duracion   = request.form.get('duracion', '').strip()
        try:
            cur.execute(
                "INSERT INTO cancion (titulo, id_artista, id_genero, album, duracion) VALUES (%s,%s,%s,%s,%s)",
                (titulo, id_artista, id_genero, album, duracion)
            )
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            cur.execute("SELECT id, nombre FROM artista WHERE lActivo=1 ORDER BY nombre")
            artistas = cur.fetchall()
            cur.execute("SELECT id, nombre FROM genero WHERE lActivo=1 ORDER BY nombre")
            generos = cur.fetchall()
            cur.close()
            return render_template('canciones/form.html', cancion=None, accion='Nueva',
                                   artistas=artistas, generos=generos, error=str(e))
        return redirect(url_for('canciones'))
    cur.execute("SELECT id, nombre FROM artista WHERE lActivo=1 ORDER BY nombre")
    artistas = cur.fetchall()
    cur.execute("SELECT id, nombre FROM genero WHERE lActivo=1 ORDER BY nombre")
    generos = cur.fetchall()
    cur.close()
    return render_template('canciones/form.html', cancion=None, accion='Nueva',
                           artistas=artistas, generos=generos, error=None)


@app.route('/canciones/editar/<int:cid>', methods=['GET', 'POST'])
@requiere_sesion
@admin_o_editor
def cancion_editar(cid):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        titulo     = request.form['titulo'].strip()
        id_artista = request.form['id_artista']
        id_genero  = request.form['id_genero']
        album      = request.form.get('album', '').strip()
        duracion   = request.form.get('duracion', '').strip()
        lActivo    = 1 if request.form.get('lActivo') else 0
        cur.execute("""
            UPDATE cancion
            SET titulo=%s, id_artista=%s, id_genero=%s, album=%s, duracion=%s, lActivo=%s
            WHERE id=%s
        """, (titulo, id_artista, id_genero, album, duracion, lActivo, cid))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('canciones'))
    cur.execute(
        "SELECT id, titulo, id_artista, id_genero, album, duracion, lActivo FROM cancion WHERE id=%s",
        (cid,)
    )
    cancion = cur.fetchone()
    cur.execute("SELECT id, nombre FROM artista WHERE lActivo=1 ORDER BY nombre")
    artistas = cur.fetchall()
    cur.execute("SELECT id, nombre FROM genero WHERE lActivo=1 ORDER BY nombre")
    generos = cur.fetchall()
    cur.close()
    return render_template('canciones/form.html', cancion=cancion, accion='Editar',
                           artistas=artistas, generos=generos, error=None)


@app.route('/canciones/eliminar/<int:cid>', methods=['POST'])
@requiere_sesion
@solo_admin
def cancion_eliminar(cid):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE cancion SET lActivo = 0 WHERE id = %s", (cid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('canciones'))


# ── Catálogo: Configuración del sistema ─────────────────────
@app.route('/config')
@requiere_sesion
def config():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, clave, valor, descripcion FROM config_sistema ORDER BY clave")
    params = cur.fetchall()
    cur.close()
    return render_template('config/index.html', params=params)


@app.route('/config/editar/<int:pid>', methods=['GET', 'POST'])
@requiere_sesion
@solo_admin
def config_editar(pid):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        valor       = request.form['valor'].strip()
        descripcion = request.form.get('descripcion', '').strip()
        cur.execute(
            "UPDATE config_sistema SET valor=%s, descripcion=%s WHERE id=%s",
            (valor, descripcion, pid)
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('config'))
    cur.execute("SELECT * FROM config_sistema WHERE id=%s", (pid,))
    param = cur.fetchone()
    cur.close()
    return render_template('config/form.html', param=param)


if __name__ == '__main__':
    app.run(port=3000, debug=True)
