from alembic.command import upgrade
from alembic.config import Config
import os

def run_migrations(): 
    migrations_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(migrations_dir, "alembic.ini")
    config = Config(file_=config_file)
    config.set_main_option("script_location", os.path.join(migrations_dir,"alembic"))
    upgrade(config, "head")
    print("migrations complete")

run_migrations()