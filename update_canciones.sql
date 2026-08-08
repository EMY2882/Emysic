-- ============================================================
--  Emysic — Actualización de artistas y canciones
--  Sin artistas repetidos en el catálogo de canciones
-- ============================================================

USE `Suemy$emysic_db`;

-- Agregar artistas nuevos
INSERT INTO artista (nombre, genero, pais, bio) VALUES
  ('Doja Cat',      'Pop / Hip-Hop', 'EE.UU.',       'Cantante y rapera reconocida por su versatilidad musical.'),
  ('Harry Styles',  'Pop / Rock',    'Reino Unido',  'Exintegrante de One Direction con exitosa carrera en solitario.'),
  ('Olivia Rodrigo','Pop / Rock',    'EE.UU.',       'Cantautora ganadora del Grammy conocida por sus letras emotivas.'),
  ('The Weeknd',    'R&B / Pop',     'Canadá',       'Artista canadiense conocido por su estilo oscuro y atmosférico.');

-- Limpiar canciones actuales
DELETE FROM cancion;

-- Insertar canciones una por artista sin repetir
INSERT INTO cancion (titulo, id_artista, id_genero, album, duracion) VALUES
  ('Bad Guy',          1,  1, 'When We All Fall Asleep', '3:14'),
  ('R U Mine?',        2,  2, 'AM',                      '3:21'),
  ('Dynamite',         3,  4, 'BE',                      '3:19'),
  ('Levitating',       4,  5, 'Future Nostalgia',        '3:23'),
  ('HUMBLE.',          5,  3, 'DAMN.',                   '2:57'),
  ('The Scientist',    6,  2, 'A Rush of Blood',         '5:09'),
  ('Kiss Me More',     7,  1, 'Planet Her',              '3:29'),
  ('Watermelon Sugar', 8,  1, 'Fine Line',               '2:54'),
  ('drivers license',  9,  1, 'SOUR',                    '4:02'),
  ('Blinding Lights',  10, 6, 'After Hours',             '3:20');
