from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigCaja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_efectivo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('actualizado_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'verbose_name': 'Configuración de caja'},
        ),
        migrations.CreateModel(
            name='CierreCaja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('apertura_en', models.DateTimeField(auto_now_add=True)),
                ('cierre_en', models.DateTimeField(blank=True, null=True)),
                ('base_efectivo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_efectivo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_tarjeta', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_transferencia', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('efectivo_contado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('diferencia', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('notas', models.TextField(blank=True)),
                ('estado', models.CharField(
                    choices=[('abierta', 'Abierta'), ('cerrada', 'Cerrada')],
                    default='abierta', max_length=10,
                )),
                ('cajero', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='cierres_caja',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Cierre de caja',
                'verbose_name_plural': 'Cierres de caja',
                'ordering': ['-apertura_en'],
            },
        ),
    ]
