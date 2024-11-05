import redis

class RedisDatabase:
    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.client = None

    def __enter__(self):
        """Estabelece a conexão ao entrar no contexto."""
        self.client = redis.StrictRedis(host=self.host, port=self.port, db=self.db, decode_responses=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha a conexão ao sair do contexto."""
        self.client = None

    def _execute_command(self, command, *args, **kwargs):
        """Executa um comando Redis e lida com exceções."""
        if not self.client:
            print("Redis connection is not established.")
            return None
        try:
            return command(*args, **kwargs)
        except Exception as e:
            print(f"Error executing command: {e}")
            return None

    def save(self, key, value, ttl=None):
        """Salva um valor no Redis com a chave especificada e um TTL opcional."""
        result = self._execute_command(self.client.set, key, value, ex=ttl)
        if result:
            print(f"Saved: {key} -> {value} with TTL: {ttl}")

    def load(self, key):
        """Carrega um valor do Redis com a chave especificada."""
        value = self._execute_command(self.client.get, key)
        if value is not None:
            print(f"Loaded: {key} -> {value}")
        else:
            print(f"No data found for key: {key}")
        return value

    def purge(self):
        """Remove todas as chaves que tenham expirado (gerenciado automaticamente pelo Redis)."""
        print("Purged expired keys (handled automatically by Redis).")

# Exemplo de uso
if __name__ == "__main__":
    with RedisDatabase() as db:
        # Salvar dados com TTL de 10 segundos
        db.save('my_key', 'my_value', ttl=10)

        # Carregar dados
        value = db.load('my_key')

        # Esperar para ver a expiração
        import time
        time.sleep(12)

        # Tentar carregar os dados novamente após o TTL
        value_after_expiration = db.load('my_key')

        # Purgar dados (não é necessário, mas podemos chamar)
        db.purge()
