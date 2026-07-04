import hashlib
import random
from datetime import datetime, timedelta


def _generar_cadena():
    ahora  = datetime.now().strftime("%Y%m%d%H%M%S")
    numero = random.randint(1, 9999)
    return f"emysic.{ahora}.{numero}"


def generar_token():
    """Retorna (cadena_original, cValor_MD5)."""
    cadena  = _generar_cadena()
    c_valor = hashlib.md5(cadena.encode("utf-8")).hexdigest()
    return cadena, c_valor


def _get_minutos(mysql):
    """Lee TOKEN_MINUTOS desde config_sistema. Default 30."""
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT valor FROM config_sistema WHERE clave = 'TOKEN_MINUTOS'"
        )
        row = cur.fetchone()
        cur.close()
        return int(row[0]) if row else 30
    except Exception:
        return 30


def crear_sesion(mysql, id_usuario):
    """
    Crea token en BD. Desactiva tokens anteriores del usuario.
    Retorna el cValor (MD5).
    """
    minutos = _get_minutos(mysql)
    cadena, c_valor = generar_token()
    d_fecha = datetime.now() + timedelta(minutes=minutos)

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE token SET lActivo = 0 WHERE idUsuario = %s",
        (id_usuario,)
    )
    cur.execute(
        """INSERT INTO token (idUsuario, cValor, cadena, dFecha, lActivo)
           VALUES (%s, %s, %s, %s, 1)""",
        (id_usuario, c_valor, cadena, d_fecha)
    )
    mysql.connection.commit()
    cur.close()
    return c_valor


def verificar_token(mysql, c_valor):
    """Verifica si el token existe, está activo y no expiró."""
    cur = mysql.connection.cursor()
    cur.execute(
        """SELECT * FROM token
           WHERE cValor = %s
             AND lActivo = 1
             AND dFecha > NOW()""",
        (c_valor,)
    )
    sesion = cur.fetchone()
    cur.close()
    return sesion


def renovar_token(mysql, c_valor):
    """Suma TOKEN_MINUTOS a dFecha si el token sigue activo."""
    minutos = _get_minutos(mysql)
    cur = mysql.connection.cursor()
    cur.execute(
        """UPDATE token
           SET dFecha = DATE_ADD(NOW(), INTERVAL %s MINUTE)
           WHERE cValor = %s
             AND lActivo = 1
             AND dFecha > NOW()""",
        (minutos, c_valor)
    )
    afectadas = cur.rowcount
    mysql.connection.commit()
    cur.close()
    return afectadas > 0


def cerrar_sesion(mysql, c_valor):
    """Marca token como inactivo (historial)."""
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE token SET lActivo = 0 WHERE cValor = %s",
        (c_valor,)
    )
    mysql.connection.commit()
    cur.close()
