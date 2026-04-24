"""
Script de datos de prueba para el sistema de restaurante.
Uso: python seed.py  (desde el directorio backend con el entorno virtual activo)
"""
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurante.settings')
django.setup()

from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.users.models import Usuario
from apps.mesas.models import Mesa
from apps.productos.models import Categoria, Producto
from apps.pedidos.models import Pedido, DetallePedido
from apps.facturacion.models import Factura, AlertaCajero
from apps.caja.models import ConfigCaja, CierreCaja

# ── Limpieza ───────────────────────────────────────────────────────────────────
print("Limpiando datos anteriores...")
AlertaCajero.objects.all().delete()
Factura.objects.all().delete()
DetallePedido.objects.all().delete()
Pedido.objects.all().delete()
Mesa.objects.all().delete()
Producto.objects.all().delete()
Categoria.objects.all().delete()
CierreCaja.objects.all().delete()
ConfigCaja.objects.all().delete()
Usuario.objects.all().delete()

# ── Usuarios ───────────────────────────────────────────────────────────────────
print("Creando usuarios...")

admin = Usuario.objects.create_superuser('admin', 'admin@restaurante.com', 'admin123')
admin.rol = 'admin'
admin.first_name = 'Carlos'
admin.last_name = 'Administrador'
admin.save()

mesero1 = Usuario.objects.create_user('mesero1', 'mesero1@restaurante.com', 'mesero123')
mesero1.rol = 'mesero'
mesero1.first_name = 'Juan'
mesero1.last_name = 'Pérez'
mesero1.save()

mesero2 = Usuario.objects.create_user('mesero2', 'mesero2@restaurante.com', 'mesero123')
mesero2.rol = 'mesero'
mesero2.first_name = 'Laura'
mesero2.last_name = 'García'
mesero2.save()

cajero = Usuario.objects.create_user('cajero1', 'cajero@restaurante.com', 'cajero123')
cajero.rol = 'cajero'
cajero.first_name = 'Ana'
cajero.last_name = 'Martínez'
cajero.save()

cocina = Usuario.objects.create_user('cocina1', 'cocina@restaurante.com', 'cocina123')
cocina.rol = 'cocina'
cocina.first_name = 'Pedro'
cocina.last_name = 'Cocinero'
cocina.save()

# ── Mesas ──────────────────────────────────────────────────────────────────────
print("Creando mesas...")

mesas = []
configs = [
    (1, 2), (2, 2), (3, 4), (4, 4), (5, 4),
    (6, 6), (7, 6), (8, 8), (9, 4), (10, 4),
]
for numero, capacidad in configs:
    mesas.append(Mesa.objects.create(numero=numero, capacidad=capacidad, estado='libre'))

# ── Categorías y Productos ─────────────────────────────────────────────────────
print("Creando categorías y productos...")

cat_entradas   = Categoria.objects.create(nombre='Entradas')
cat_sopas      = Categoria.objects.create(nombre='Sopas')
cat_principales = Categoria.objects.create(nombre='Platos Principales')
cat_bebidas    = Categoria.objects.create(nombre='Bebidas')
cat_postres    = Categoria.objects.create(nombre='Postres')

# requiere_cocina=True  -> aparece en pantalla de cocina
# requiere_cocina=False -> el mesero puede entregarlo directamente sin esperar cocina
productos_data = [
    # (nombre, descripcion, precio, categoria, requiere_cocina)
    # Entradas
    ('Empanadas de pipián (3 und)', 'Empanadas fritas rellenas de pipián',   Decimal('8500'),  cat_entradas,    True),
    ('Patacones con hogao',         'Patacones crujientes con salsa hogao',   Decimal('7000'),  cat_entradas,    True),
    ('Aguacate relleno',            'Aguacate relleno con atún y verduras',   Decimal('12000'), cat_entradas,    False),
    # Sopas
    ('Ajiaco santafereño',          'Sopa tradicional con pollo y guascas',   Decimal('18000'), cat_sopas,       True),
    ('Sancocho de gallina',         'Caldo de gallina con papas y yuca',      Decimal('16000'), cat_sopas,       True),
    ('Caldo de costilla',           'Caldo tradicional con costilla de res',  Decimal('12000'), cat_sopas,       True),
    # Platos principales
    ('Bandeja paisa',               'Frijoles, chicharrón, carne, chorizo',   Decimal('35000'), cat_principales, True),
    ('Trucha al ajillo',            'Trucha fresca al ajillo con ensalada',   Decimal('32000'), cat_principales, True),
    ('Pollo asado',                 'Pollo asado al carbón con arroz',        Decimal('28000'), cat_principales, True),
    ('Lomo de res',                 'Lomo de res a la plancha con papa',      Decimal('42000'), cat_principales, True),
    ('Churrasco',                   'Churrasco 300g con chimichurri',         Decimal('45000'), cat_principales, True),
    ('Pasta carbonara',             'Pasta con salsa carbonara y tocineta',   Decimal('22000'), cat_principales, True),
    # Bebidas (no requieren cocina — el mesero las entrega directamente)
    ('Jugo natural',                'Jugo de fruta natural (mora, lulo...)',  Decimal('6000'),  cat_bebidas,     False),
    ('Limonada de coco',            'Limonada con crema de coco',             Decimal('8000'),  cat_bebidas,     False),
    ('Agua mineral',                'Agua mineral 500ml',                     Decimal('3500'),  cat_bebidas,     False),
    ('Gaseosa',                     'Gaseosa 350ml (Coca-Cola, Sprite)',      Decimal('4000'),  cat_bebidas,     False),
    ('Cerveza nacional',            'Cerveza 330ml (Club Colombia, Águila)',  Decimal('6500'),  cat_bebidas,     False),
    ('Café americano',              'Café de origen colombiano',              Decimal('4500'),  cat_bebidas,     False),
    # Postres (no requieren cocina — ya están preparados)
    ('Tres leches',                 'Torta tres leches casera',               Decimal('9000'),  cat_postres,     False),
    ('Brownie con helado',          'Brownie de chocolate con helado',        Decimal('11000'), cat_postres,     False),
    ('Flan de caramelo',            'Flan casero con salsa de caramelo',      Decimal('8000'),  cat_postres,     False),
]

productos = []
for nombre, desc, precio, cat, req_cocina in productos_data:
    productos.append(Producto.objects.create(
        nombre=nombre,
        descripcion=desc,
        precio=precio,
        categoria=cat,
        requiere_cocina=req_cocina,
    ))

# Referencias por nombre para claridad
empanadas, patacones, aguacate = productos[0], productos[1], productos[2]
ajiaco, sancocho, caldo        = productos[3], productos[4], productos[5]
bandeja, trucha, pollo         = productos[6], productos[7], productos[8]
lomo, churrasco, pasta         = productos[9], productos[10], productos[11]
jugo, limonada, agua           = productos[12], productos[13], productos[14]
gaseosa, cerveza, cafe         = productos[15], productos[16], productos[17]
tres_leches, brownie, flan     = productos[18], productos[19], productos[20]

ahora = timezone.now()

# ── Pedidos de ejemplo ─────────────────────────────────────────────────────────
print("Creando pedidos de ejemplo...")

# ── Pedido 1: Mesa 3 — estado LISTO (cocina terminó, mesero puede entregar) ──
mesa3 = mesas[2]
mesa3.estado = 'ocupada'
mesa3.save()

p1 = Pedido.objects.create(
    mesa=mesa3, mesero=mesero1, estado='listo',
    en_preparacion_en=ahora - timedelta(minutes=25),
    listo_en=ahora - timedelta(minutes=5),
)
# Items de cocina: listos pero no entregados aún
DetallePedido.objects.create(pedido=p1, producto=bandeja,    cantidad=2, precio_unitario=bandeja.precio,    entregado=False)
DetallePedido.objects.create(pedido=p1, producto=ajiaco,     cantidad=1, precio_unitario=ajiaco.precio,     entregado=False)
# Bebidas: ya entregadas (no requieren cocina, el mesero las sirvió al llegar)
DetallePedido.objects.create(pedido=p1, producto=limonada,   cantidad=2, precio_unitario=limonada.precio,   entregado=True)
DetallePedido.objects.create(pedido=p1, producto=cerveza,    cantidad=1, precio_unitario=cerveza.precio,    entregado=True)

# ── Pedido 2: Mesa 3 — pedido ADICIONAL pendiente (misma mesa que p1) ─────────
p2 = Pedido.objects.create(
    mesa=mesa3, mesero=mesero1, estado='pendiente',
)
DetallePedido.objects.create(pedido=p2, producto=tres_leches, cantidad=2, precio_unitario=tres_leches.precio, entregado=False)
DetallePedido.objects.create(pedido=p2, producto=brownie,     cantidad=1, precio_unitario=brownie.precio,     entregado=False)
DetallePedido.objects.create(pedido=p2, producto=cafe,        cantidad=2, precio_unitario=cafe.precio,        entregado=False)

# ── Pedido 3: Mesa 5 — estado EN PREPARACIÓN (cocina trabajando) ──────────────
mesa5 = mesas[4]
mesa5.estado = 'ocupada'
mesa5.save()

p3 = Pedido.objects.create(
    mesa=mesa5, mesero=mesero2, estado='en_preparacion',
    en_preparacion_en=ahora - timedelta(minutes=12),
)
DetallePedido.objects.create(pedido=p3, producto=trucha,   cantidad=2, precio_unitario=trucha.precio,   entregado=False)
DetallePedido.objects.create(pedido=p3, producto=sancocho, cantidad=1, precio_unitario=sancocho.precio, entregado=False)
# Bebidas ya entregadas
DetallePedido.objects.create(pedido=p3, producto=jugo,     cantidad=2, precio_unitario=jugo.precio,     entregado=True)

# ── Pedido 4: Mesa 7 — estado PENDIENTE (recién enviado a cocina) ─────────────
mesa7 = mesas[6]
mesa7.estado = 'ocupada'
mesa7.save()

p4 = Pedido.objects.create(
    mesa=mesa7, mesero=mesero1, estado='pendiente',
)
DetallePedido.objects.create(pedido=p4, producto=empanadas, cantidad=2, precio_unitario=empanadas.precio, entregado=False)
DetallePedido.objects.create(pedido=p4, producto=lomo,      cantidad=1, precio_unitario=lomo.precio,      entregado=False)
DetallePedido.objects.create(pedido=p4, producto=churrasco, cantidad=1, precio_unitario=churrasco.precio, entregado=False)
# Bebidas entregadas al tomar el pedido
DetallePedido.objects.create(pedido=p4, producto=agua,      cantidad=2, precio_unitario=agua.precio,      entregado=True)
DetallePedido.objects.create(pedido=p4, producto=gaseosa,   cantidad=2, precio_unitario=gaseosa.precio,   entregado=True)

# ── Pedido 5: Mesa 1 — PAGADO con factura (historial) ────────────────────────
mesa1 = mesas[0]
# mesa1 queda libre (ya fue pagado)

p5 = Pedido.objects.create(
    mesa=mesa1, mesero=mesero2, estado='pagado',
    en_preparacion_en=ahora - timedelta(hours=2, minutes=30),
    listo_en=ahora - timedelta(hours=2),
    entregado_en=ahora - timedelta(hours=1, minutes=45),
)
DetallePedido.objects.create(pedido=p5, producto=pollo,      cantidad=1, precio_unitario=pollo.precio,      entregado=True)
DetallePedido.objects.create(pedido=p5, producto=pasta,      cantidad=1, precio_unitario=pasta.precio,      entregado=True)
DetallePedido.objects.create(pedido=p5, producto=gaseosa,    cantidad=2, precio_unitario=gaseosa.precio,    entregado=True)
DetallePedido.objects.create(pedido=p5, producto=brownie,    cantidad=1, precio_unitario=brownie.precio,    entregado=True)

subtotal5 = p5.calcular_subtotal()
iva_pct   = Decimal('19')
base5     = subtotal5
total5    = base5 * (1 + iva_pct / 100)
Factura.objects.create(
    pedido=p5,
    cajero=cajero,
    subtotal=subtotal5,
    descuento=Decimal('0'),
    propina=Decimal('0'),
    iva=iva_pct,
    total=total5,
    metodo_pago='efectivo',
    extras=[],
    extras_total=Decimal('0'),
)

# ── Caja ───────────────────────────────────────────────────────────────────────
print("Configurando caja...")

ConfigCaja.objects.create(
    base_efectivo=Decimal('100000'),
    actualizado_por=admin,
)

CierreCaja.objects.create(
    cajero=cajero,
    base_efectivo=Decimal('100000'),
    total_efectivo=total5,   # lo cobrado en el pedido pagado
    total_tarjeta=Decimal('0'),
    total_transferencia=Decimal('0'),
    estado='abierta',
)

# ── Resumen ────────────────────────────────────────────────────────────────────
print("\nDatos de prueba creados exitosamente.\n")
print("=" * 50)
print("USUARIOS DE PRUEBA")
print("=" * 50)
print("  admin    / admin123   -> Dashboard Admin")
print("  mesero1  / mesero123  -> Dashboard Mesero (Juan Pérez)")
print("  mesero2  / mesero123  -> Dashboard Mesero (Laura García)")
print("  cajero1  / cajero123  -> Dashboard Cajero")
print("  cocina1  / cocina123  -> Dashboard Cocina")
print("=" * 50)
print(f"  Mesas creadas:    {Mesa.objects.count()}")
print(f"  Productos:        {Producto.objects.count()}  (bebidas y postres sin cocina)")
print(f"  Categorías:       {Categoria.objects.count()}")
print(f"  Pedidos:          {Pedido.objects.count()}")
print(f"    -> Mesa 3: pedido LISTO + pedido adicional PENDIENTE")
print(f"    -> Mesa 5: pedido EN PREPARACIÓN")
print(f"    -> Mesa 7: pedido PENDIENTE")
print(f"    -> Mesa 1: pedido PAGADO (historial)")
print(f"  Facturas:         {Factura.objects.count()}")
print(f"  Caja:             abierta (base $100.000)")
print("=" * 50)
