USE emysic_db;
ALTER TABLE usuario 
MODIFY COLUMN rol ENUM('admin','editor','viewer') NOT NULL DEFAULT 'viewer';

DROP TABLE IF EXISTS config_sistema;
CREATE TABLE config_sistema (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    clave       VARCHAR(100) NOT NULL UNIQUE,
    valor       VARCHAR(255) NOT NULL,
    descripcion VARCHAR(255)
);

INSERT INTO config_sistema (clave, valor, descripcion) VALUES
  ('TOKEN_MINUTOS', '30',    'Tiempo de vida del token en minutos'),
  ('APP_NOMBRE',    'Emysic', 'Nombre de la aplicación'),
  ('MAX_INTENTOS',  '5',     'Intentos máximos de login');

-- ------------------------------------------------------------
-- 2. Usuarios del sistema
-- ------------------------------------------------------------
DROP TABLE IF EXISTS usuario;
CREATE TABLE usuario (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(80)  NOT NULL UNIQUE,
    email      VARCHAR(150) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    rol        ENUM('admin','editor','viewer') NOT NULL DEFAULT 'viewer',
    lActivo    TINYINT(1) NOT NULL DEFAULT 1,
    fecha_alta DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Usuario: emy  |  Contraseña: Admin1234!
INSERT INTO usuario (username, email, password, rol) VALUES
  ('emy', 'suemyum.ms24@universidadupp.edu.mx',
   'scrypt:32768:8:1$fXAMOJ9T1WKo2pHa$b16747964668d426c0fe93690bd6921570f43d90fa45cb8abf6bed26b9d595afaed2773dce517bdc35d4218a6f0f5c8282f16c7375a4c8d514606d39f893225e',
   'admin');

-- ------------------------------------------------------------
-- 3. Artistas
-- ------------------------------------------------------------
DROP TABLE IF EXISTS artista;
CREATE TABLE artista (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(150) NOT NULL,
    genero     VARCHAR(100),
    pais       VARCHAR(100),
    bio        TEXT,
    lActivo    TINYINT(1) NOT NULL DEFAULT 1,
    fecha_alta DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO artista (nombre, genero, pais, bio) VALUES
  ('Billie Eilish',  'Pop / R&B',          'EE.UU.',       'Cantautora multiganadora del Grammy, conocida por su estilo oscuro y minimalista.'),
  ('Arctic Monkeys', 'Rock / Alternativo',  'Reino Unido',  'Banda británica referente del rock alternativo moderno.'),
  ('BTS',            'K-Pop',              'Corea del Sur', 'Grupo de K-Pop más influyente a nivel mundial con millones de fanáticos.'),
  ('Dua Lipa',       'Pop / Electrónica',   'Reino Unido',  'Cantante reconocida por sus éxitos de pop dance a nivel global.'),
  ('Kendrick Lamar', 'Hip-Hop',            'EE.UU.',       'Rapero ganador del Premio Pulitzer, considerado uno de los mejores del género.');

-- ------------------------------------------------------------
-- 4. Tokens de sesión
-- ------------------------------------------------------------
DROP TABLE IF EXISTS token;
CREATE TABLE token (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    idUsuario INT         NOT NULL,
    cValor    VARCHAR(32) NOT NULL UNIQUE,
    cadena    VARCHAR(255) NOT NULL,
    dFecha    DATETIME    NOT NULL,
    lActivo   TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (idUsuario) REFERENCES usuario(id) ON DELETE CASCADE
);
