import os
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


class ConexionBD:

    def __init__(self, path_env: str):
        self.path_env = path_env
        self.tunnel = None
        self.engine = None

    def conectar(self, db_name: str):

        # 1️⃣ Validar que exista el archivo de credenciales
        if not os.path.exists(self.path_env):
            raise FileNotFoundError(f"No existe el archivo: {self.path_env}")

        # 2️⃣ Cargar variables
        load_dotenv(self.path_env, override=True)

        required_vars = [
            "SSH_HOST",
            "SSH_PORT",
            "SSH_USER",
            "SSH_KEY_FILE",
            "SSH_KEY_PASSPHRASE",
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
        SSH_KEY_PASSPHRASE = os.getenv("SSH_KEY_PASSPHRASE")

        REMOTE_DB_HOST = os.getenv("REMOTE_DB_HOST")
        REMOTE_DB_PORT = int(os.getenv("REMOTE_DB_PORT"))

        LOCAL_BIND_HOST = os.getenv("LOCAL_BIND_HOST", "127.0.0.1")
        LOCAL_BIND_PORT = int(os.getenv("LOCAL_BIND_PORT", 0))

        DB_USER = os.getenv("DB_USER")
        DB_PASS = os.getenv("DB_PASS")

        # 3️⃣ Construir ruta del PEM relativa al archivo .txt
        base_dir = os.path.dirname(os.path.abspath(self.path_env))
        SSH_KEY_PATH = os.path.join(base_dir, SSH_KEY_FILE)

        if not os.path.exists(SSH_KEY_PATH):
            raise FileNotFoundError(f"No existe el archivo PEM: {SSH_KEY_PATH}")

        # 4️⃣ Crear túnel SSH
        self.tunnel = SSHTunnelForwarder(
            (SSH_HOST, SSH_PORT),
            ssh_username=SSH_USER,
            ssh_pkey=SSH_KEY_PATH,
            ssh_private_key_password=SSH_KEY_PASSPHRASE,
            remote_bind_address=(REMOTE_DB_HOST, REMOTE_DB_PORT),
            local_bind_address=(LOCAL_BIND_HOST, LOCAL_BIND_PORT)
        )

        self.tunnel.start()

        # 5️⃣ Crear engine SQLAlchemy
        connection_string = (
            f"mysql+pymysql://{DB_USER}:{DB_PASS}"
            f"@127.0.0.1:{self.tunnel.local_bind_port}/{db_name}"
        )

        self.engine = create_engine(connection_string, pool_pre_ping=True)

        # 6️⃣ Validar conexión real y existencia de la base
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            if self.engine:
                self.engine.dispose()
            if self.tunnel:
                self.tunnel.stop()
            raise ConnectionError(
                f"La base '{db_name}' no existe o las credenciales son inválidas."
            )

        print(f"✅ Conectado a base: {db_name}")

        return self.engine

    def cerrar(self):

        if self.engine:
            self.engine.dispose()
            print("🔒 Engine cerrado")

        if self.tunnel:
            self.tunnel.stop()
            print("🔒 Túnel SSH cerrado")