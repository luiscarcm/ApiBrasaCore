from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import Usuario
from apps.mesas.models import Mesa
from apps.productos.models import Categoria, Producto
from apps.pedidos.models import Pedido, DetallePedido
from apps.facturacion.models import Factura, AlertaCajero
from apps.caja.models import ConfigCaja, CierreCaja
from apps.inventario.models import (
    CategoriaIngrediente, Ingrediente, RecetaProducto, MovimientoInventario
)


class Command(BaseCommand):
    help = 'Carga datos de prueba. Solo corre si no hay usuarios creados.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Forzar seed aunque ya existan datos')

    def handle(self, *args, **options):
        if Usuario.objects.exists() and not options['force']:
            self.stdout.write('Ya existen datos. Usa --force para recargar.')
            return

        self.stdout.write('Limpiando datos anteriores...')
        MovimientoInventario.objects.all().delete()
        RecetaProducto.objects.all().delete()
        Ingrediente.objects.all().delete()
        CategoriaIngrediente.objects.all().delete()
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

        # ── Usuarios ──────────────────────────────────────────────────────────
        self.stdout.write('Creando usuarios...')
        admin = Usuario.objects.create_superuser('admin', 'admin@restaurante.com', 'admin123')
        admin.rol = 'admin'; admin.first_name = 'Carlos'; admin.last_name = 'Administrador'; admin.save()

        mesero1 = Usuario.objects.create_user('mesero1', 'mesero1@restaurante.com', 'mesero123')
        mesero1.rol = 'mesero'; mesero1.first_name = 'Juan'; mesero1.last_name = 'Pérez'; mesero1.save()

        mesero2 = Usuario.objects.create_user('mesero2', 'mesero2@restaurante.com', 'mesero123')
        mesero2.rol = 'mesero'; mesero2.first_name = 'Laura'; mesero2.last_name = 'García'; mesero2.save()

        cajero = Usuario.objects.create_user('cajero1', 'cajero@restaurante.com', 'cajero123')
        cajero.rol = 'cajero'; cajero.first_name = 'Ana'; cajero.last_name = 'Martínez'; cajero.save()

        cocina = Usuario.objects.create_user('cocina1', 'cocina@restaurante.com', 'cocina123')
        cocina.rol = 'cocina'; cocina.first_name = 'Pedro'; cocina.last_name = 'Cocinero'; cocina.save()

        # ── Mesas ─────────────────────────────────────────────────────────────
        self.stdout.write('Creando mesas...')
        mesas = []
        for numero, capacidad in [(1,2),(2,2),(3,4),(4,4),(5,4),(6,6),(7,6),(8,8),(9,4),(10,4)]:
            mesas.append(Mesa.objects.create(numero=numero, capacidad=capacidad, estado='libre'))

        # ── Categorías y Productos ────────────────────────────────────────────
        self.stdout.write('Creando categorías y productos...')
        cat_entradas    = Categoria.objects.create(nombre='Entradas')
        cat_sopas       = Categoria.objects.create(nombre='Sopas')
        cat_principales = Categoria.objects.create(nombre='Platos Principales')
        cat_bebidas     = Categoria.objects.create(nombre='Bebidas')
        cat_postres     = Categoria.objects.create(nombre='Postres')

        def prod(nombre, desc, precio, cat, req_cocina):
            return Producto.objects.create(
                nombre=nombre, descripcion=desc,
                precio=Decimal(precio), categoria=cat, requiere_cocina=req_cocina
            )

        empanadas   = prod('Empanadas de pipián (3 und)', 'Empanadas fritas rellenas de pipián',   '8500',  cat_entradas,    True)
        patacones   = prod('Patacones con hogao',         'Patacones crujientes con salsa hogao',   '7000',  cat_entradas,    True)
        aguacate    = prod('Aguacate relleno',            'Aguacate relleno con atún y verduras',   '12000', cat_entradas,    False)
        ajiaco      = prod('Ajiaco santafereño',          'Sopa tradicional con pollo y guascas',   '18000', cat_sopas,       True)
        sancocho    = prod('Sancocho de gallina',         'Caldo de gallina con papas y yuca',      '16000', cat_sopas,       True)
        caldo       = prod('Caldo de costilla',           'Caldo tradicional con costilla de res',  '12000', cat_sopas,       True)
        bandeja     = prod('Bandeja paisa',               'Frijoles, chicharrón, carne, chorizo',   '35000', cat_principales, True)
        trucha      = prod('Trucha al ajillo',            'Trucha fresca al ajillo con ensalada',   '32000', cat_principales, True)
        pollo_prod  = prod('Pollo asado',                 'Pollo asado al carbón con arroz',        '28000', cat_principales, True)
        lomo        = prod('Lomo de res',                 'Lomo de res a la plancha con papa',      '42000', cat_principales, True)
        churrasco   = prod('Churrasco',                   'Churrasco 300g con chimichurri',         '45000', cat_principales, True)
        pasta       = prod('Pasta carbonara',             'Pasta con salsa carbonara y tocineta',   '22000', cat_principales, True)
        jugo        = prod('Jugo natural',                'Jugo de fruta natural (mora, lulo...)',  '6000',  cat_bebidas,     False)
        limonada    = prod('Limonada de coco',            'Limonada con crema de coco',             '8000',  cat_bebidas,     False)
        agua        = prod('Agua mineral',                'Agua mineral 500ml',                     '3500',  cat_bebidas,     False)
        gaseosa     = prod('Gaseosa',                     'Gaseosa 350ml (Coca-Cola, Sprite)',      '4000',  cat_bebidas,     False)
        cerveza     = prod('Cerveza nacional',            'Cerveza 330ml (Club Colombia, Águila)',  '6500',  cat_bebidas,     False)
        cafe        = prod('Café americano',              'Café de origen colombiano',              '4500',  cat_bebidas,     False)
        tres_leches = prod('Tres leches',                 'Torta tres leches casera',               '9000',  cat_postres,     False)
        brownie     = prod('Brownie con helado',          'Brownie de chocolate con helado',        '11000', cat_postres,     False)
        flan        = prod('Flan de caramelo',            'Flan casero con salsa de caramelo',      '8000',  cat_postres,     False)

        # ── Inventario: Categorías de ingredientes ────────────────────────────
        self.stdout.write('Creando inventario...')
        ci_carnes   = CategoriaIngrediente.objects.create(nombre='Carnes y Proteínas')
        ci_lacteos  = CategoriaIngrediente.objects.create(nombre='Lácteos')
        ci_verduras = CategoriaIngrediente.objects.create(nombre='Verduras y Tubérculos')
        ci_granos   = CategoriaIngrediente.objects.create(nombre='Granos y Harinas')
        ci_liquidos = CategoriaIngrediente.objects.create(nombre='Bebidas y Líquidos')
        ci_salsas   = CategoriaIngrediente.objects.create(nombre='Salsas y Condimentos')

        # ── Ingredientes (stock_actual, stock_minimo, stock_critico) ──────────
        # Estado OK
        def ing(nombre, unidad, actual, minimo, critico, categoria):
            return Ingrediente.objects.create(
                nombre=nombre, unidad_medida=unidad,
                stock_actual=Decimal(str(actual)),
                stock_minimo=Decimal(str(minimo)),
                stock_critico=Decimal(str(critico)),
                categoria=categoria
            )

        # Carnes y proteínas
        pechuga_pollo = ing('Pechuga de pollo',    'kg',  8.0,   3.0,  1.0,  ci_carnes)
        lomo_res      = ing('Lomo de res',         'kg',  5.0,   2.0,  0.5,  ci_carnes)
        costilla_res  = ing('Costilla de res',     'kg',  4.0,   2.0,  0.5,  ci_carnes)
        chorizo       = ing('Chorizo',             'kg',  2.0,   1.0,  0.3,  ci_carnes)
        chicharron    = ing('Chicharrón',          'kg',  1.5,   1.0,  0.3,  ci_carnes)
        trucha_ing    = ing('Trucha entera',       'kg',  3.0,   2.0,  0.5,  ci_carnes)
        atun_lata     = ing('Atún en lata',        'unidad', 6, 4,    2,    ci_carnes)
        # Lácteos
        crema_leche   = ing('Crema de leche',      'l',   4.0,   2.0,  0.5,  ci_lacteos)
        leche         = ing('Leche entera',        'l',   5.0,   2.0,  1.0,  ci_lacteos)
        mantequilla   = ing('Mantequilla',         'kg',  1.0,   0.5,  0.2,  ci_lacteos)
        queso_crema   = ing('Queso crema',         'kg',  0.8,   0.5,  0.2,  ci_lacteos)
        # Verduras y tubérculos — algunos en stock bajo/crítico para demo
        papa_criolla  = ing('Papa criolla',        'kg',  10.0,  5.0,  2.0,  ci_verduras)
        yuca          = ing('Yuca',                'kg',  6.0,   3.0,  1.0,  ci_verduras)
        platano       = ing('Plátano verde',       'kg',  4.0,   2.0,  1.0,  ci_verduras)
        aguacate_ing  = ing('Aguacate',            'unidad', 8, 5,    2,    ci_verduras)
        cebolla       = ing('Cebolla cabezona',    'kg',  3.0,   2.0,  0.5,  ci_verduras)
        tomate        = ing('Tomate chonto',       'kg',  2.0,   2.0,  0.5,  ci_verduras)   # BAJO
        lechuga       = ing('Lechuga',             'unidad', 2, 3,    1,    ci_verduras)    # BAJO
        guascas       = ing('Guascas (paquete)',   'unidad', 1, 2,    1,    ci_verduras)    # CRITICO
        # Granos y harinas
        arroz         = ing('Arroz blanco',        'kg',  15.0,  5.0,  2.0,  ci_granos)
        frijoles      = ing('Frijoles rojos',      'kg',  5.0,   3.0,  1.0,  ci_granos)
        harina_trigo  = ing('Harina de trigo',     'kg',  4.0,   2.0,  0.5,  ci_granos)
        pasta_ing     = ing('Pasta (espagueti)',   'kg',  3.0,   1.5,  0.5,  ci_granos)
        # Bebidas y líquidos — algunos críticos para demo
        agua_mineral  = ing('Agua mineral (botella)', 'unidad', 24, 12,  6,  ci_liquidos)
        gaseosa_ing   = ing('Gaseosa (botella)',   'unidad', 18, 12,  6,    ci_liquidos)
        cerveza_ing   = ing('Cerveza (botella)',   'unidad', 4,  12,  6,    ci_liquidos)    # CRITICO
        cafe_molido   = ing('Café molido',         'kg',  0.3,   0.5,  0.2,  ci_liquidos)   # CRITICO
        leche_coco    = ing('Leche de coco',       'l',   2.0,   1.0,  0.3,  ci_liquidos)
        limon         = ing('Limón',               'unidad', 20, 10,  5,    ci_liquidos)
        # Salsas y condimentos
        sal           = ing('Sal',                 'kg',  2.0,   1.0,  0.3,  ci_salsas)
        aceite        = ing('Aceite vegetal',      'l',   3.0,   1.5,  0.5,  ci_salsas)
        ajo           = ing('Ajo',                 'kg',  0.5,   0.3,  0.1,  ci_salsas)
        chimichurri   = ing('Chimichurri (frasco)','unidad', 2, 2,    1,    ci_salsas)     # BAJO
        tocineta      = ing('Tocineta',            'kg',  0.4,   0.5,  0.2,  ci_salsas)    # BAJO

        # ── Recetas ───────────────────────────────────────────────────────────
        self.stdout.write('Creando recetas...')

        def receta(producto, ingrediente, cantidad):
            RecetaProducto.objects.create(
                producto=producto,
                ingrediente=ingrediente,
                cantidad=Decimal(str(cantidad))
            )

        # Bandeja paisa (por porción)
        receta(bandeja, frijoles,    Decimal('0.150'))
        receta(bandeja, arroz,       Decimal('0.200'))
        receta(bandeja, chicharron,  Decimal('0.100'))
        receta(bandeja, chorizo,     Decimal('0.100'))
        receta(bandeja, lomo_res,    Decimal('0.150'))
        receta(bandeja, aceite,      Decimal('0.030'))

        # Ajiaco santafereño
        receta(ajiaco, pechuga_pollo, Decimal('0.200'))
        receta(ajiaco, papa_criolla,  Decimal('0.300'))
        receta(ajiaco, guascas,       Decimal('0.010'))
        receta(ajiaco, cebolla,       Decimal('0.050'))

        # Sancocho de gallina
        receta(sancocho, pechuga_pollo, Decimal('0.250'))
        receta(sancocho, yuca,          Decimal('0.200'))
        receta(sancocho, papa_criolla,  Decimal('0.200'))
        receta(sancocho, cebolla,       Decimal('0.050'))

        # Trucha al ajillo
        receta(trucha, trucha_ing,  Decimal('0.400'))
        receta(trucha, ajo,         Decimal('0.020'))
        receta(trucha, mantequilla, Decimal('0.030'))
        receta(trucha, lechuga,     Decimal('0.250'))

        # Pollo asado
        receta(pollo_prod, pechuga_pollo, Decimal('0.350'))
        receta(pollo_prod, arroz,         Decimal('0.200'))
        receta(pollo_prod, ajo,           Decimal('0.015'))
        receta(pollo_prod, aceite,        Decimal('0.020'))

        # Lomo de res
        receta(lomo, lomo_res,     Decimal('0.350'))
        receta(lomo, papa_criolla, Decimal('0.200'))
        receta(lomo, aceite,       Decimal('0.020'))
        receta(lomo, sal,          Decimal('0.010'))

        # Churrasco
        receta(churrasco, lomo_res,   Decimal('0.350'))
        receta(churrasco, chimichurri,Decimal('0.050'))
        receta(churrasco, aceite,     Decimal('0.020'))

        # Pasta carbonara
        receta(pasta, pasta_ing,   Decimal('0.150'))
        receta(pasta, tocineta,    Decimal('0.080'))
        receta(pasta, crema_leche, Decimal('0.100'))
        receta(pasta, mantequilla, Decimal('0.020'))

        # Patacones con hogao
        receta(patacones, platano, Decimal('0.300'))
        receta(patacones, aceite,  Decimal('0.050'))
        receta(patacones, tomate,  Decimal('0.100'))
        receta(patacones, cebolla, Decimal('0.050'))

        # Caldo de costilla
        receta(caldo, costilla_res, Decimal('0.300'))
        receta(caldo, papa_criolla, Decimal('0.200'))
        receta(caldo, cebolla,      Decimal('0.050'))

        # Aguacate relleno
        receta(aguacate, aguacate_ing, Decimal('1.000'))
        receta(aguacate, atun_lata,    Decimal('1.000'))
        receta(aguacate, tomate,       Decimal('0.080'))

        # Limonada de coco
        receta(limonada, limon,      Decimal('3.000'))
        receta(limonada, leche_coco, Decimal('0.100'))

        # Café americano
        receta(cafe, cafe_molido, Decimal('0.015'))
        receta(cafe, agua_mineral, Decimal('0.200'))

        # ── Movimientos iniciales de stock ────────────────────────────────────
        self.stdout.write('Registrando entradas iniciales de inventario...')
        for ingrediente in Ingrediente.objects.all():
            if ingrediente.stock_actual > 0:
                MovimientoInventario.objects.create(
                    ingrediente=ingrediente,
                    tipo='entrada',
                    cantidad=ingrediente.stock_actual,
                    stock_resultante=ingrediente.stock_actual,
                    usuario=admin,
                    notas='Stock inicial — carga de datos de prueba'
                )

        # ── Pedidos ───────────────────────────────────────────────────────────
        self.stdout.write('Creando pedidos...')
        ahora = timezone.now()

        mesa3 = mesas[2]; mesa3.estado = 'ocupada'; mesa3.save()
        p1 = Pedido.objects.create(mesa=mesa3, mesero=mesero1, estado='listo',
            en_preparacion_en=ahora-timedelta(minutes=25), listo_en=ahora-timedelta(minutes=5))
        DetallePedido.objects.create(pedido=p1, producto=bandeja,    cantidad=2, precio_unitario=bandeja.precio,    entregado=False)
        DetallePedido.objects.create(pedido=p1, producto=ajiaco,     cantidad=1, precio_unitario=ajiaco.precio,     entregado=False)
        DetallePedido.objects.create(pedido=p1, producto=limonada,   cantidad=2, precio_unitario=limonada.precio,   entregado=True)
        DetallePedido.objects.create(pedido=p1, producto=cerveza,    cantidad=1, precio_unitario=cerveza.precio,    entregado=True)

        p2 = Pedido.objects.create(mesa=mesa3, mesero=mesero1, estado='pendiente')
        DetallePedido.objects.create(pedido=p2, producto=tres_leches, cantidad=2, precio_unitario=tres_leches.precio, entregado=False)
        DetallePedido.objects.create(pedido=p2, producto=brownie,     cantidad=1, precio_unitario=brownie.precio,     entregado=False)
        DetallePedido.objects.create(pedido=p2, producto=cafe,        cantidad=2, precio_unitario=cafe.precio,        entregado=False)

        mesa5 = mesas[4]; mesa5.estado = 'ocupada'; mesa5.save()
        p3 = Pedido.objects.create(mesa=mesa5, mesero=mesero2, estado='en_preparacion',
            en_preparacion_en=ahora-timedelta(minutes=12))
        DetallePedido.objects.create(pedido=p3, producto=trucha,   cantidad=2, precio_unitario=trucha.precio,   entregado=False)
        DetallePedido.objects.create(pedido=p3, producto=sancocho, cantidad=1, precio_unitario=sancocho.precio, entregado=False)
        DetallePedido.objects.create(pedido=p3, producto=jugo,     cantidad=2, precio_unitario=jugo.precio,     entregado=True)

        mesa7 = mesas[6]; mesa7.estado = 'ocupada'; mesa7.save()
        p4 = Pedido.objects.create(mesa=mesa7, mesero=mesero1, estado='pendiente')
        DetallePedido.objects.create(pedido=p4, producto=empanadas, cantidad=2, precio_unitario=empanadas.precio, entregado=False)
        DetallePedido.objects.create(pedido=p4, producto=lomo,      cantidad=1, precio_unitario=lomo.precio,      entregado=False)
        DetallePedido.objects.create(pedido=p4, producto=churrasco, cantidad=1, precio_unitario=churrasco.precio, entregado=False)
        DetallePedido.objects.create(pedido=p4, producto=agua,      cantidad=2, precio_unitario=agua.precio,      entregado=True)
        DetallePedido.objects.create(pedido=p4, producto=gaseosa,   cantidad=2, precio_unitario=gaseosa.precio,   entregado=True)

        p5 = Pedido.objects.create(mesa=mesas[0], mesero=mesero2, estado='pagado',
            en_preparacion_en=ahora-timedelta(hours=2, minutes=30),
            listo_en=ahora-timedelta(hours=2),
            entregado_en=ahora-timedelta(hours=1, minutes=45))
        DetallePedido.objects.create(pedido=p5, producto=pollo_prod, cantidad=1, precio_unitario=pollo_prod.precio, entregado=True)
        DetallePedido.objects.create(pedido=p5, producto=pasta,      cantidad=1, precio_unitario=pasta.precio,      entregado=True)
        DetallePedido.objects.create(pedido=p5, producto=gaseosa,    cantidad=2, precio_unitario=gaseosa.precio,    entregado=True)
        DetallePedido.objects.create(pedido=p5, producto=brownie,    cantidad=1, precio_unitario=brownie.precio,    entregado=True)

        # ── Factura ───────────────────────────────────────────────────────────
        subtotal5 = p5.calcular_subtotal()
        total5 = subtotal5 * Decimal('1.19')
        Factura.objects.create(
            pedido=p5, cajero=cajero, subtotal=subtotal5,
            descuento=Decimal('0'), propina=Decimal('0'), iva=Decimal('19'),
            total=total5, metodo_pago='efectivo', extras=[], extras_total=Decimal('0')
        )

        # Alerta de cajero de ejemplo (ítem removido en pedido anterior)
        p6 = Pedido.objects.create(mesa=mesas[1], mesero=mesero2, estado='pagado',
            en_preparacion_en=ahora-timedelta(hours=4),
            listo_en=ahora-timedelta(hours=3, minutes=40),
            entregado_en=ahora-timedelta(hours=3, minutes=20))
        det6 = DetallePedido.objects.create(pedido=p6, producto=trucha, cantidad=1, precio_unitario=trucha.precio, entregado=True)
        DetallePedido.objects.create(pedido=p6, producto=agua, cantidad=2, precio_unitario=agua.precio, entregado=True)
        subtotal6 = p6.calcular_subtotal()
        Factura.objects.create(
            pedido=p6, cajero=cajero, subtotal=subtotal6,
            descuento=Decimal('10'), propina=Decimal('0'), iva=Decimal('19'),
            total=subtotal6 * Decimal('0.9') * Decimal('1.19'),
            metodo_pago='tarjeta', extras=[], extras_total=Decimal('0')
        )
        AlertaCajero.objects.create(
            pedido=p6, cajero=cajero,
            descripcion='El cliente devolvió la trucha porque llegó fría. Se retiró del cobro y se aplicó descuento del 10%.',
            items_removidos=[{
                'nombre': 'Trucha al ajillo',
                'cantidad': 1,
                'precio_unitario': str(trucha.precio),
                'motivo': 'Producto devuelto — llegó frío'
            }],
            leido=False
        )

        # ── Caja ─────────────────────────────────────────────────────────────
        ConfigCaja.objects.create(base_efectivo=Decimal('100000'), actualizado_por=admin)
        CierreCaja.objects.create(
            cajero=cajero,
            base_efectivo=Decimal('100000'),
            total_efectivo=total5,
            total_tarjeta=subtotal6 * Decimal('0.9') * Decimal('1.19'),
            total_transferencia=Decimal('0'),
            estado='abierta'
        )

        criticos = sum(1 for i in Ingrediente.objects.all() if i.estado_stock == 'critico')
        bajos    = sum(1 for i in Ingrediente.objects.all() if i.estado_stock == 'bajo')

        self.stdout.write(self.style.SUCCESS(f"""
Datos cargados exitosamente.
  Usuarios:           {Usuario.objects.count()}
  Mesas:              {Mesa.objects.count()}
  Categorías menú:    {Categoria.objects.count()}
  Productos:          {Producto.objects.count()}
  Pedidos:            {Pedido.objects.count()}
  Facturas:           {Factura.objects.count()}
  Alertas cajero:     {AlertaCajero.objects.count()}
  Cat. ingredientes:  {CategoriaIngrediente.objects.count()}
  Ingredientes:       {Ingrediente.objects.count()} ({criticos} críticos, {bajos} bajos)
  Recetas:            {RecetaProducto.objects.count()} líneas
  Movimientos inv.:   {MovimientoInventario.objects.count()}

Ingredientes con alerta:
  CRITICO: Guascas, Cerveza (botella), Café molido
  BAJO:    Tomate, Lechuga, Chimichurri, Tocineta

Credenciales:
  admin    / admin123   → Panel Administrador
  mesero1  / mesero123  → Dashboard Mesero (Juan Pérez)
  mesero2  / mesero123  → Dashboard Mesero (Laura García)
  cajero1  / cajero123  → Dashboard Cajero
  cocina1  / cocina123  → Pantalla Cocina
        """))
