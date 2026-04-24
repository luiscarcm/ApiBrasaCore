from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0003_alertacajero'),
    ]

    operations = [
        migrations.AddField(
            model_name='factura',
            name='extras',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='factura',
            name='extras_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
