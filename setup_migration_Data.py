from django.db import migrations, models

operations = [
    ('API', 'previous_migration')
]

operations = [
    migrations.RunSQL("""
	INSERT INTO prendas
	VALUES ('','','','')
	""","""
    INSERT INTO prendas
	VALUES ('','','','')
    """)

]

# ![Heroku Config Variables](/config_vars.png "Heroku config vars")