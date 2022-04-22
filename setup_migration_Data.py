from django.db import migrations, models

operations = [
    ('API', 'previous_migration')
]

operations = [
    migrations.RunSQL("""
	INSERT INTO prendas
	VALUES ('','','','')
	""","""
    INSERT INTO telas
	VALUES ('','','','')
    """)

]