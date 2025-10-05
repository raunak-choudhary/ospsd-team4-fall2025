import pathlib

p = pathlib.Path("src/mail_client_service/tests/__init__.py")
p.parent.mkdir(parents=True, exist_ok=True)
p.touch()
print("Ensured tests package is importable")
