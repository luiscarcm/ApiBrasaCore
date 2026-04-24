from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import Usuario
from apps.mesas.models import Mesa
from apps.productos.models import Categoria, Producto
from apps.pedidos.models import Pedido, DetallePedido
from apps.facturacion.models import Factura
from apps.caja.models import ConfigCaja, CierreCaja


class Command(BaseCommand):
    help = 'Carga datos de prueba. Solo corre si no hay usuarios creados.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Forzar seed aunque ya existan datos')

    def handle(self, *args, **options):
        if Usuario.objects.exists() and not options['force']:
            self.stdout.write('Ya existen datos. Usa --force para recargar.')
            return

        self.stdout.write('Limpiando datos anteriores...')
        try:
            from apps.facturacion.models import AlertaCajero
            AlertaCajero.objects.all().delete()
        except Exception:
            pass
        Factura.objects.all().delete()
        DetallePedido.objects.all().delete()
        Pedido.objects.all().delete()
        Mesa.objects.all().delete()
        Producto.objects.all().delete()
        Categoria.objects.all().delete()
        CierreCaja.objects.all().delete()
        ConfigCaja.objects.all().delete()
        Usuario.objects.all().delete()

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

        self.stdout.write('Creando mesas...')
        mesas = []
        for numero, capacidad in [(1,2),(2,2),(3,4),(4,4),(5,4),(6,6),(7,6),(8,8),(9,4),(10,4)]:
            mesas.append(Mesa.objects.create(numero=numero, capacidad=capacidad, estado='libre'))

        self.stdout.write('Creando productos...')
        cat_entradas    = Categoria.objects.create(nombre='Entradas')
        cat_sopas       = Categoria.objects.create(nombre='Sopas')
        cat_principales = Categoria.objects.create(nombre='Platos Principales')
        cat_bebidas     = Categoria.objects.create(nombre='Bebidas')
        cat_postres     = Categoria.objects.create(nombre='Postres')

        def p(nombre, desc, precio, cat, cocina):
            return Producto.objects.create(nombre=nombre, descripcion=desc, precio=Decimal(precio), categoria=cat, requiere_cocina=cocina)

        empanadas = p('Empanadas de pipián (3 und)', 'Empanadas fritas rellenas de pipián',   '8500',  cat_entradas,    True)
        patacones = p('Patacones con hogao',         'Patacones crujientes con salsa hogao',   '7000',  cat_entradas,    True)
        aguacate  = p('Aguacate relleno',            'Aguacate relleno con atún y verduras',   '12000', cat_entradas,    False)
        ajiaco    = p('Ajiaco santafereño',          'Sopa tradicional con pollo y guascas',   '18000', cat_sopas,       True)
        sancocho  = p('Sancocho de gallina',         'Caldo de gallina con papas y yuca',      '16000', cat_sopas,       True)
        caldo     = p('Caldo de costilla',           'Caldo tradicional con costilla de res',  '12000', cat_sopas,       True)
        bandeja   = p('Bandeja paisa',               'Frijoles, chicharrón, carne, chorizo',   '35000', cat_principales, True)
        trucha    = p('Trucha al ajillo',            'Trucha fresca al ajillo con ensalada',   '32000', cat_principales, True)
        pollo     = p('Pollo asado',                 'Pollo asado al carbón con arroz',        '28000', cat_principales, True)
        lomo      = p('Lomo de res',                 'Lomo de res a la plancha con papa',      '42000', cat_principales, True)
        churrasco = p('Churrasco',                   'Churrasco 300g con chimichurri',         '45000', cat_principales, True)
        pasta     = p('Pasta carbonara',             'Pasta con salsa carbonara y tocineta',   '22000', cat_principales, True)
        jugo      = p('Jugo natural',                'Jugo de fruta natural (mora, lulo...)',  '6000',  cat_bebidas,     False)
        limonada  = p('Limonada de coco',            'Limonada con crema de coco',             '8000',  cat_bebidas,     False)
        agua      = p('Agua mineral',                'Agua mineral 500ml',                     '3500',  cat_bebidas,     False)
        gaseosa   = p('Gaseosa',                     'Gaseosa 350ml (Coca-Cola, Sprite)',      '4000',  cat_bebidas,     False)
        cerveza   = p('Cerveza nacional',            'Cerveza 330ml (Club Colombia, Águila)',  '6500',  cat_bebidas,     False)
        cafe      = p('Café americano',              'Café de origen colombiano',              '4500',  cat_bebidas,     False)
        tres_leches = p('Tres leches',               'Torta tres leches casera',               '9000',  cat_postres,     False)
        brownie   = p('Brownie con helado',          'Brownie de chocolate con helado',        '11000', cat_postres,     False)
        flan      = p('Flan de caramelo',            'Flan casero con salsa de caramelo',      '8000',  cat_postres,     False)

        self.stdout.write('Creando pedidos...')
        ahora = timezone.now()

        mesa3 = mesas[2]; mesa3.estado = 'ocupada'; mesa3.save()
        p1 = Pedido.objects.create(mesa=mesa3, mesero=mesero1, estado='listo',
            en_preparacion_en=ahora-timedelta(minutes=25), listo_en=ahora-timedelta(minutes=5))
        DetallePedido.objects.create(pedido=p1, producto=bandeja,  cantidad=2, precio_unitario=bandeja.precio,  entregado=False)
        DetallePedido.objects.create(pedido=p1, producto=ajiaco,   cantidad=1, precio_unitario=ajiaco.precio,   entregado=False)
        DetallePedido.objects.create(pedido=p1, producto=limonada, cantidad=2, precio_unitario=limonada.precio, entregado=True)
        DetallePedido.objects.create(pedido=p1, producto=cerveza,  cantidad=1, precio_unitario=cerveza.precio,  entregado=True)

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
        DetallePedido.objects.create(pedido=p5, producto=pollo,   cantidad=1, precio_unitario=pollo.precio,   entregado=True)
        DetallePedido.objects.create(pedido=p5, producto=pasta,   cantidad=1, precio_unitario=pasta.precio,   entregado=True)
        DetallePedido.objects.create(pedido=p5, producto=gaseosa, cantidad=2, precio_unitario=gaseosa.precio, entregado=True)
        DetallePedido.objects.create(pedido=p5, producto=brownie, cantidad=1, precio_unitario=brownie.precio, entregado=True)

        subtotal5 = p5.calcular_subtotal()
        total5 = subtotal5 * Decimal('1.19')
        Factura.objects.create(pedido=p5, cajero=cajero, subtotal=subtotal5,
            descuento=Decimal('0'), propina=Decimal('0'), iva=Decimal('19'),
            total=total5, metodo_pago='efectivo', extras=[], extras_total=Decimal('0'))

        ConfigCaja.objects.create(base_efectivo=Decimal('100000'), actualizado_por=admin)
        CierreCaja.objects.create(cajero=cajero, base_efectivo=Decimal('100000'),
            total_efectivo=total5, total_tarjeta=Decimal('0'),
            total_transferencia=Decimal('0'), estado='abierta')

        self.stdout.write(self.style.SUCCESS(f"""
Datos cargados exitosamente.
  Usuarios:   {Usuario.objects.count()}
  Mesas:      {Mesa.objects.count()}
  Productos:  {Producto.objects.count()}
  Pedidos:    {Pedido.objects.count()}
  Facturas:   {Factura.objects.count()}

Credenciales:
  admin    / admin123
  mesero1  / mesero123
  cajero1  / cajero123
  cocina1  / cocina123
        """))
