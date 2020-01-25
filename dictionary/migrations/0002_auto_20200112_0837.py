# Generated by Django 3.0.2 on 2020-01-12 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mandarinword',
            old_name='definition',
            new_name='definitions',
        ),
        migrations.AddField(
            model_name='mandarinword',
            name='similar_words',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
    ]
