from django.db import models
from apps.users.models import Usuario
from apps.productos.models import Producto


class CategoriaIngrediente(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Categoría de Ingrediente'
        verbose_name_plural = 'Categorías de Ingredientes'

    def __str__(self):
        return self.nombre


class Ingrediente(models.Model):
    UNIDAD_CHOICES = [
        ('g', 'Gramos'),
        ('kg', 'Kilogramos'),
        ('ml', 'Mililitros'),
        ('l', 'Litros'),
        ('unidad', 'Unidades'),
        ('porcion', 'Porciones'),
    ]
    nombre = models.CharField(max_length=200)
    unidad_medida = models.CharField(max_length=20, choices=UNIDAD_CHOICES, default='unidad')
    stock_actual = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    stock_critico = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    categoria = models.ForeignKey(
        CategoriaIngrediente,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ingredientes'
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'

    def __str__(self):
        return f"{self.nombre} ({self.unidad_medida})"

    @property
    def estado_stock(self):
        if self.stock_actual <= self.stock_critico:
            return 'critico'
        if self.stock_actual <= self.stock_minimo:
            return 'bajo'
        return 'ok'


class RecetaProducto(models.Model):
    """Ingredientes requeridos para preparar una unidad de un Producto."""
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='receta'
    )
    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.CASCADE,
        related_name='en_recetas'
    )
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        unique_together = ('producto', 'ingrediente')
        verbose_name = 'Receta'
        verbose_name_plural = 'Recetas'

    def __str__(self):
        return (
            f"{self.producto.nombre} → "
            f"{self.cantidad} {self.ingrediente.unidad_medida} "
            f"de {self.ingrediente.nombre}"
        )


class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada de stock'),
        ('salida_pedido', 'Consumo por pedido'),
        ('devolucion_pedido', 'Devolución de pedido'),
        ('ajuste_manual', 'Ajuste manual'),
    ]
    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.CASCADE,
        related_name='movimientos'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    stock_resultante = models.DecimalField(max_digits=12, decimal_places=3)
    referencia_pedido = models.ForeignKey(
        'pedidos.Pedido',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movimientos_inventario'
    )
    referencia_detalle = models.ForeignKey(
        'pedidos.DetallePedido',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movimientos_inventario'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movimientos_inventario'
    )
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.ingrediente.nombre}: {self.cantidad}"
