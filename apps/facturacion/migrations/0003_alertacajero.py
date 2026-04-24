from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pedidos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertaCajero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField()),
                ('items_removidos', models.JSONField(default=list)),
                ('leido', models.BooleanField(default=False)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('cajero', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='alertas',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('pedido', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='alertas',
                    to='pedidos.pedido',
                )),
            ],
            options={
                'verbose_name': 'Alerta de Cajero',
                'verbose_name_plural': 'Alertas de Cajero',
                'ordering': ['-creado_en'],
            },
        ),
    ]
