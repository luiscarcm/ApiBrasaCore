from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0003_pedido_en_preparacion_en_pedido_entregado_en_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallepedido',
            name='entregado',
            field=models.BooleanField(default=False),
        ),
    ]
