import unittest
from unittest.mock import patch, MagicMock
from your_module import RedisDatabase  # Altere para o nome do seu módulo

class TestRedisDatabase(unittest.TestCase):

    @patch('redis.StrictRedis')
    def setUp(self, MockRedis):
        self.db = RedisDatabase()
        self.db.client = MockRedis.return_value

    def test_save_with_ttl(self):
        self.db.save('my_key', 'my_value', ttl=10)
        self.db.client.set.assert_called_once_with('my_key', 'my_value', ex=10)

    def test_save_without_ttl(self):
        self.db.save('my_key', 'my_value')
        self.db.client.set.assert_called_once_with('my_key', 'my_value', ex=None)

    def test_load_existing_key(self):
        self.db.client.get.return_value = 'my_value'
        value = self.db.load('my_key')
        self.assertEqual(value, 'my_value')
        self.db.client.get.assert_called_once_with('my_key')

    def test_load_non_existing_key(self):
        self.db.client.get.return_value = None
        value = self.db.load('non_existing_key')
        self.assertIsNone(value)
        self.db.client.get.assert_called_once_with('non_existing_key')

    def test_purge(self):
        with patch('builtins.print') as mocked_print:
            self.db.purge()
            mocked_print.assert_called_once_with("Purged expired keys (handled automatically by Redis).")

if __name__ == '__main__':
    unittest.main()
