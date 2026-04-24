-- =============================================================================
-- SEED DATA - BrasaCore Restaurant System
-- =============================================================================
-- IMPORTANTE: Las contraseñas están en formato hash de Django (PBKDF2-SHA256).
-- Credenciales:
--   admin    / admin123
--   mesero1  / mesero123
--   mesero2  / mesero123
--   cajero1  / cajero123
--   cocina1  / cocina123
-- =============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------------------------------
-- Limpiar datos existentes (en orden por dependencias)
-- -----------------------------------------------------------------------------
TRUNCATE TABLE caja_cierrecaja;
TRUNCATE TABLE caja_configcaja;
TRUNCATE TABLE facturacion_alertacajero;
TRUNCATE TABLE facturacion_factura;
TRUNCATE TABLE pedidos_detallepedido;
TRUNCATE TABLE pedidos_pedido;
TRUNCATE TABLE mesas_mesa;
TRUNCATE TABLE productos_producto;
TRUNCATE TABLE productos_categoria;
TRUNCATE TABLE users_passwordresettoken;
TRUNCATE TABLE users_usuario;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- Usuarios
-- -----------------------------------------------------------------------------
INSERT INTO users_usuario
  (id, password, last_login, is_superuser, username, first_name, last_name,
   email, is_staff, is_active, date_joined, rol)
VALUES
  (1,
   'pbkdf2_sha256$720000$seed$admin123hash000000000000000000000000000000000=',
   NULL, 1, 'admin', 'Carlos', 'Administrador',
   'admin@restaurante.com', 1, 1, NOW(), 'admin'),
  (2,
   'pbkdf2_sha256$720000$seed$mesero1hash0000000000000000000000000000000000=',
   NULL, 0, 'mesero1', 'Juan', 'Pérez',
   'mesero1@restaurante.com', 0, 1, NOW(), 'mesero'),
  (3,
   'pbkdf2_sha256$720000$seed$mesero2hash0000000000000000000000000000000000=',
   NULL, 0, 'mesero2', 'Laura', 'García',
   'mesero2@restaurante.com', 0, 1, NOW(), 'mesero'),
  (4,
   'pbkdf2_sha256$720000$seed$cajero1hash0000000000000000000000000000000000=',
   NULL, 0, 'cajero1', 'Ana', 'Martínez',
   'cajero@restaurante.com', 0, 1, NOW(), 'cajero'),
  (5,
   'pbkdf2_sha256$720000$seed$cocina1hash0000000000000000000000000000000000=',
   NULL, 0, 'cocina1', 'Pedro', 'Cocinero',
   'cocina@restaurante.com', 0, 1, NOW(), 'cocina');

-- IMPORTANTE: Después de ejecutar este SQL, establece las contraseñas reales
-- corriendo en el shell de Railway:
--   python manage.py shell -c "
--   from apps.users.models import Usuario
--   for u, pwd in [('admin','admin123'),('mesero1','mesero123'),
--                  ('mesero2','mesero123'),('cajero1','cajero123'),('cocina1','cocina123')]:
--       usr = Usuario.objects.get(username=u); usr.set_password(pwd); usr.save()
--   print('Contraseñas actualizadas')
--   "

-- -----------------------------------------------------------------------------
-- Mesas
-- -----------------------------------------------------------------------------
INSERT INTO mesas_mesa (id, numero, capacidad, estado) VALUES
  (1,  1, 2, 'libre'),
  (2,  2, 2, 'libre'),
  (3,  3, 4, 'ocupada'),
  (4,  4, 4, 'libre'),
  (5,  5, 4, 'ocupada'),
  (6,  6, 6, 'libre'),
  (7,  7, 6, 'ocupada'),
  (8,  8, 8, 'libre'),
  (9,  9, 4, 'libre'),
  (10,10, 4, 'libre');

-- -----------------------------------------------------------------------------
-- Categorías
-- -----------------------------------------------------------------------------
INSERT INTO productos_categoria (id, nombre) VALUES
  (1, 'Entradas'),
  (2, 'Sopas'),
  (3, 'Platos Principales'),
  (4, 'Bebidas'),
  (5, 'Postres');

-- -----------------------------------------------------------------------------
-- Productos  (categoria_id, activo, requiere_cocina)
-- -----------------------------------------------------------------------------
INSERT INTO productos_producto (id, nombre, descripcion, precio, categoria_id, activo, requiere_cocina) VALUES
  -- Entradas
  (1,  'Empanadas de pipián (3 und)', 'Empanadas fritas rellenas de pipián',   8500.00,  1, 1, 1),
  (2,  'Patacones con hogao',         'Patacones crujientes con salsa hogao',   7000.00,  1, 1, 1),
  (3,  'Aguacate relleno',            'Aguacate relleno con atún y verduras',  12000.00,  1, 1, 0),
  -- Sopas
  (4,  'Ajiaco santafereño',          'Sopa tradicional con pollo y guascas',  18000.00,  2, 1, 1),
  (5,  'Sancocho de gallina',         'Caldo de gallina con papas y yuca',     16000.00,  2, 1, 1),
  (6,  'Caldo de costilla',           'Caldo tradicional con costilla de res', 12000.00,  2, 1, 1),
  -- Platos Principales
  (7,  'Bandeja paisa',               'Frijoles, chicharrón, carne, chorizo',  35000.00,  3, 1, 1),
  (8,  'Trucha al ajillo',            'Trucha fresca al ajillo con ensalada',  32000.00,  3, 1, 1),
  (9,  'Pollo asado',                 'Pollo asado al carbón con arroz',       28000.00,  3, 1, 1),
  (10, 'Lomo de res',                 'Lomo de res a la plancha con papa',     42000.00,  3, 1, 1),
  (11, 'Churrasco',                   'Churrasco 300g con chimichurri',        45000.00,  3, 1, 1),
  (12, 'Pasta carbonara',             'Pasta con salsa carbonara y tocineta',  22000.00,  3, 1, 1),
  -- Bebidas (no requieren cocina)
  (13, 'Jugo natural',                'Jugo de fruta natural (mora, lulo...)',  6000.00,  4, 1, 0),
  (14, 'Limonada de coco',            'Limonada con crema de coco',             8000.00,  4, 1, 0),
  (15, 'Agua mineral',                'Agua mineral 500ml',                     3500.00,  4, 1, 0),
  (16, 'Gaseosa',                     'Gaseosa 350ml (Coca-Cola, Sprite)',      4000.00,  4, 1, 0),
  (17, 'Cerveza nacional',            'Cerveza 330ml (Club Colombia, Águila)',  6500.00,  4, 1, 0),
  (18, 'Café americano',              'Café de origen colombiano',              4500.00,  4, 1, 0),
  -- Postres (no requieren cocina)
  (19, 'Tres leches',                 'Torta tres leches casera',               9000.00,  5, 1, 0),
  (20, 'Brownie con helado',          'Brownie de chocolate con helado',        11000.00,  5, 1, 0),
  (21, 'Flan de caramelo',            'Flan casero con salsa de caramelo',      8000.00,  5, 1, 0);

-- -----------------------------------------------------------------------------
-- Pedidos
-- -----------------------------------------------------------------------------
INSERT INTO pedidos_pedido
  (id, mesa_id, mesero_id, estado, creado_en, actualizado_en,
   en_preparacion_en, listo_en, entregado_en)
VALUES
  -- P1: Mesa 3 — LISTO (cocina terminó)
  (1, 3, 2, 'listo',
   NOW() - INTERVAL 30 MINUTE, NOW() - INTERVAL 5 MINUTE,
   NOW() - INTERVAL 25 MINUTE, NOW() - INTERVAL 5 MINUTE, NULL),
  -- P2: Mesa 3 — PENDIENTE adicional (misma mesa)
  (2, 3, 2, 'pendiente',
   NOW() - INTERVAL 5 MINUTE, NOW() - INTERVAL 5 MINUTE,
   NULL, NULL, NULL),
  -- P3: Mesa 5 — EN PREPARACIÓN
  (3, 5, 3, 'en_preparacion',
   NOW() - INTERVAL 15 MINUTE, NOW() - INTERVAL 12 MINUTE,
   NOW() - INTERVAL 12 MINUTE, NULL, NULL),
  -- P4: Mesa 7 — PENDIENTE
  (4, 7, 2, 'pendiente',
   NOW() - INTERVAL 10 MINUTE, NOW() - INTERVAL 10 MINUTE,
   NULL, NULL, NULL),
  -- P5: Mesa 1 — PAGADO (historial)
  (5, 1, 3, 'pagado',
   NOW() - INTERVAL 3 HOUR, NOW() - INTERVAL 90 MINUTE,
   NOW() - INTERVAL 150 MINUTE, NOW() - INTERVAL 120 MINUTE,
   NOW() - INTERVAL 105 MINUTE);

-- -----------------------------------------------------------------------------
-- Detalles de Pedido
-- -----------------------------------------------------------------------------
INSERT INTO pedidos_detallepedido
  (pedido_id, producto_id, cantidad, precio_unitario, observaciones, entregado)
VALUES
  -- P1: Mesa 3 listo
  (1,  7, 2, 35000.00, '', 0),  -- Bandeja paisa x2
  (1,  4, 1, 18000.00, '', 0),  -- Ajiaco x1
  (1, 14, 2,  8000.00, '', 1),  -- Limonada x2 (ya entregada)
  (1, 17, 1,  6500.00, '', 1),  -- Cerveza x1 (ya entregada)
  -- P2: Mesa 3 adicional
  (2, 19, 2,  9000.00, '', 0),  -- Tres leches x2
  (2, 20, 1, 11000.00, '', 0),  -- Brownie x1
  (2, 18, 2,  4500.00, '', 0),  -- Café x2
  -- P3: Mesa 5 en preparación
  (3,  8, 2, 32000.00, '', 0),  -- Trucha x2
  (3,  5, 1, 16000.00, '', 0),  -- Sancocho x1
  (3, 13, 2,  6000.00, '', 1),  -- Jugo x2 (ya entregado)
  -- P4: Mesa 7 pendiente
  (4,  1, 2,  8500.00, '', 0),  -- Empanadas x2
  (4, 10, 1, 42000.00, '', 0),  -- Lomo de res x1
  (4, 11, 1, 45000.00, '', 0),  -- Churrasco x1
  (4, 15, 2,  3500.00, '', 1),  -- Agua x2 (ya entregada)
  (4, 16, 2,  4000.00, '', 1),  -- Gaseosa x2 (ya entregada)
  -- P5: Mesa 1 pagado
  (5,  9, 1, 28000.00, '', 1),  -- Pollo asado x1
  (5, 12, 1, 22000.00, '', 1),  -- Pasta carbonara x1
  (5, 16, 2,  4000.00, '', 1),  -- Gaseosa x2
  (5, 20, 1, 11000.00, '', 1);  -- Brownie x1

-- -----------------------------------------------------------------------------
-- Factura (pedido 5 pagado)
-- subtotal = 28000 + 22000 + 8000 + 11000 = 69000
-- total    = 69000 * 1.19 = 82110
-- -----------------------------------------------------------------------------
INSERT INTO facturacion_factura
  (pedido_id, cajero_id, subtotal, descuento, propina, iva, total,
   metodo_pago, extras, extras_total, creado_en)
VALUES
  (5, 4, 69000.00, 0.00, 0.00, 19.00, 82110.00, 'efectivo', '[]', 0.00, NOW() - INTERVAL 90 MINUTE);

-- -----------------------------------------------------------------------------
-- Caja
-- -----------------------------------------------------------------------------
INSERT INTO caja_configcaja (id, base_efectivo, actualizado_por_id, actualizado_en)
VALUES (1, 100000.00, 1, NOW());

INSERT INTO caja_cierrecaja
  (cajero_id, apertura_en, cierre_en, base_efectivo, total_efectivo,
   total_tarjeta, total_transferencia, efectivo_contado, diferencia, notas, estado)
VALUES
  (4, NOW() - INTERVAL 8 HOUR, NULL, 100000.00, 82110.00,
   0.00, 0.00, NULL, NULL, '', 'abierta');

-- =============================================================================
-- FIN DEL SCRIPT
-- =============================================================================
-- Resumen:
--   Usuarios:    5  (admin, mesero1, mesero2, cajero1, cocina1)
--   Mesas:      10
--   Categorías:  5
--   Productos:  21
--   Pedidos:     5  (mesa3: listo + pendiente | mesa5: en_preparacion | mesa7: pendiente | mesa1: pagado)
--   Facturas:    1
--   Caja:        abierta con base $100.000
-- =============================================================================
