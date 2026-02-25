import os
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
from sqlalchemy import create_engine


class ConexionBD:

    def __init__(self, path_env: str):
        self.path_env = path_env
        self.tunnel = None
        self.engine = None

    def conectar(self, db_name: str):

        # Validar que exista el archivo
        if not os.path.exists(self.path_env):
            raise FileNotFoundError(f"No existe el archivo: {self.path_env}")

        # Cargar variables del archivo
        load_dotenv(self.path_env)

        required_vars = [
            "SSH_HOST",
            "SSH_PORT",
            "SSH_USER",
            "SSH_KEY_FILE",
            "REMOTE_DB_HOST",
            "REMOTE_DB_PORT",
            "DB_USER",
            "DB_PASS",
        ]

        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Faltan variables en el archivo: {missing}")

        SSH_HOST = os.getenv("SSH_HOST")
        SSH_PORT = int(os.getenv("SSH_PORT"))
        SSH_USER = os.getenv("SSH_USER")
        SSH_KEY_FILE = os.getenv("SSH_KEY_FILE")

        REMOTE_DB_HOST = os.getenv("REMOTE_DB_HOST")
        REMOTE_DB_PORT = int(os.getenv("REMOTE_DB_PORT"))

        DB_USER = os.getenv("DB_USER")
        DB_PASS = os.getenv("DB_PASS")

        # 🔐 Construir ruta del .pem relativa al archivo .txt
        base_dir = os.path.dirname(os.path.abspath(self.path_env))
        SSH_KEY_PATH = os.path.join(base_dir, SSH_KEY_FILE)

        if not os.path.exists(SSH_KEY_PATH):
            raise FileNotFoundError(f"No existe el archivo PEM: {SSH_KEY_PATH}")

        # 1️⃣ Crear túnel SSH
        self.tunnel = SSHTunnelForwarder(
            (SSH_HOST, SSH_PORT),
            ssh_username=SSH_USER,
            ssh_pkey=SSH_KEY_PATH,
            remote_bind_address=(REMOTE_DB_HOST, REMOTE_DB_PORT),
            local_bind_address=("127.0.0.1", 0)
        )

        self.tunnel.start()

        # 2️⃣ Crear engine SQLAlchemy
        connection_string = (
            f"mysql+pymysql://{DB_USER}:{DB_PASS}"
            f"@127.0.0.1:{self.tunnel.local_bind_port}/{db_name}"
        )

        self.engine = create_engine(connection_string, pool_pre_ping=True)

        print(f"✅ Conectado a base: {db_name}")

        return self.engine

    def cerrar(self):

        if self.engine:
            self.engine.dispose()
            print("🔒 Engine cerrado")

        if self.tunnel:
            self.tunnel.stop()
            print("🔒 Túnel SSH cerrado")