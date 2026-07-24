from django.contrib.auth.hashers import make_password
from django.db import migrations


def promote_superuser(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    email = "muneneemmanuel953@gmail.com"
    user = User.objects.filter(email=email).first()
    if user:
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=["is_staff", "is_superuser"])
    else:
        User.objects.create(
            email=email,
            username=email.split("@")[0],
            password=make_password("Admin123!"),
            is_verified=True,
            is_staff=True,
            is_superuser=True,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [migrations.RunPython(promote_superuser)]
