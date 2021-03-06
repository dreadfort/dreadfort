import unittest

from mock import MagicMock
from mock import patch

from dreadfort.data.cache_handler import Cache
from dreadfort.data.cache_handler import CACHE_CONFIG
from dreadfort.data.cache_handler import CACHE_TENANT
from dreadfort.data.cache_handler import CACHE_TOKEN
from dreadfort.data.cache_handler import ConfigCache
from dreadfort.data.cache_handler import CONFIG_EXPIRES
from dreadfort.data.cache_handler import DEFAULT_EXPIRES
from dreadfort.data.cache_handler import TenantCache
from dreadfort.data.cache_handler import TokenCache
from dreadfort.data.cache_handler import NativeProxy
from dreadfort.data.model.tenant import Tenant
from dreadfort.data.model.tenant import Token
from dreadfort.data.model.worker import WorkerConfiguration
from dreadfort.openstack.common import jsonutils


def suite():
    suite = unittest.TestSuite()
    suite.addTest(WhenTestingBaseCache())
    suite.addTest(WhenTestingConfigCache())
    suite.addTest(WhenTestingTenantCache())
    return suite


class WhenTestingBaseCache(unittest.TestCase):

    def test_cache_raises_not_implemented(self):
        cache = Cache()
        with self.assertRaises(NotImplementedError):
            cache.clear()


class WhenTestingConfigCache(unittest.TestCase):

    def setUp(self):
        self.cache_clear = MagicMock()
        self.cache_true = MagicMock(return_value=True)
        self.cache_false = MagicMock(return_value=False)
        self.cache_update = MagicMock()
        self.cache_set = MagicMock()
        self.cache_del = MagicMock()
        self.config = WorkerConfiguration(
            personality='worker',
            hostname='worker01',
            coordinator_uri='http://192.168.1.2/v1')
        self.config_json = jsonutils.dumps(self.config.format())
        self.cache_get_config = MagicMock(return_value=self.config_json)

    def test_clear_calls_cache_clear(self):
        with patch.object(NativeProxy, 'cache_clear', self.cache_clear):
            config_cache = ConfigCache()
            config_cache.clear()
        self.cache_clear.assert_called_once_with(CACHE_CONFIG)

    def test_set_config_calls_cache_update(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_true
        ), patch.object(NativeProxy, 'cache_update', self.cache_update):
            config_cache = ConfigCache()
            config_cache.set_config(self.config)

        self.cache_update.assert_called_once_with(
            'worker_configuration', jsonutils.dumps(self.config.format()),
            CONFIG_EXPIRES, CACHE_CONFIG)

    def test_set_config_calls_cache_set(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_false
        ), patch.object(NativeProxy, 'cache_set', self.cache_set):
            config_cache = ConfigCache()
            config_cache.set_config(self.config)

        self.cache_set.assert_called_once_with(
            'worker_configuration', jsonutils.dumps(self.config.format()),
            CONFIG_EXPIRES, CACHE_CONFIG)

    def test_get_config_calls_returns_config(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_true
        ), patch.object(NativeProxy, 'cache_get',  self.cache_get_config):
            config_cache = ConfigCache()
            config = config_cache.get_config()

        self.cache_get_config.assert_called_once_with(
            'worker_configuration', CACHE_CONFIG)
        self.assertIsInstance(config, WorkerConfiguration)

    def test_get_config_calls_returns_none(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_false):
            config_cache = ConfigCache()
            config = config_cache.get_config()

        self.assertIs(config, None)

    def test_delete_config_calls_cache_del(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_true
        ), patch.object(NativeProxy, 'cache_del', self.cache_del):
            config_cache = ConfigCache()
            config_cache.delete_config()

        self.cache_del.assert_called_once_with(
            'worker_configuration', CACHE_CONFIG)

    def test_delete_config_does_not_call_cache_del(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_false
        ), patch.object(NativeProxy, 'cache_del', self.cache_del):
            config_cache = ConfigCache()
            config_cache.delete_config()

        with self.assertRaises(AssertionError):
            self.cache_del.assert_called_once_with(
                'worker_configuration', CACHE_CONFIG)


class WhenTestingTenantCache(unittest.TestCase):

    def setUp(self):
        self.cache_clear = MagicMock()
        self.cache_true = MagicMock(return_value=True)
        self.cache_false = MagicMock(return_value=False)
        self.cache_update = MagicMock()
        self.cache_set = MagicMock()
        self.cache_del = MagicMock()
        self.tenant_id = '101'
        self.tenant = Tenant(
            tenant_id=self.tenant_id,
            token=Token()
        )
        self.tenant_json = jsonutils.dumps(self.tenant.format())
        self.cache_get_tenant = MagicMock(return_value=self.tenant_json)

    def test_clear_calls_cache_clear(self):
        with patch.object(NativeProxy, 'cache_clear', self.cache_clear):
            tenant_cache = TenantCache()
            tenant_cache.clear()
        self.cache_clear.assert_called_once_with(CACHE_TENANT)

    def test_set_tenant_calls_cache_update(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_true
        ), patch.object(NativeProxy, 'cache_update', self.cache_update):
            tenant_cache = TenantCache()
            tenant_cache.set_tenant(self.tenant)

        self.cache_update.assert_called_once_with(
            self.tenant_id, jsonutils.dumps(self.tenant.format()),
            DEFAULT_EXPIRES, CACHE_TENANT)

    def test_set_tenant_calls_cache_set(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_false
        ), patch.object(NativeProxy, 'cache_set', self.cache_set):
            tenant_cache = TenantCache()
            tenant_cache.set_tenant(self.tenant)

        self.cache_set.assert_called_once_with(
            self.tenant_id, jsonutils.dumps(self.tenant.format()),
            DEFAULT_EXPIRES, CACHE_TENANT)

    def test_get_tenant_calls_returns_tenant(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_true
        ), patch.object(NativeProxy, 'cache_get',  self.cache_get_tenant):
            tenant_cache = TenantCache()
            tenant = tenant_cache.get_tenant(self.tenant_id)

        self.cache_get_tenant.assert_called_once_with(
            self.tenant_id, CACHE_TENANT)
        self.assertIsInstance(tenant, Tenant)

    def test_get_tenant_calls_returns_none(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_false):
            tenant_cache = TenantCache()
            tenant = tenant_cache.get_tenant(self.tenant_id)

        self.assertIs(tenant, None)

    def test_delete_tenant_calls_cache_del(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_true
        ), patch.object(NativeProxy, 'cache_del', self.cache_del):
            tenant_cache = TenantCache()
            tenant_cache.delete_tenant(self.tenant_id)

        self.cache_del.assert_called_once_with(
            self.tenant_id, CACHE_TENANT)

    def test_delete_tenant_does_not_call_cache_del(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_false
        ), patch.object(NativeProxy, 'cache_del', self.cache_del):
            tenant_cache = TenantCache()
            tenant_cache.delete_tenant(self.tenant_id)

        with self.assertRaises(AssertionError):
            self.cache_del.assert_called_once_with(
                self.tenant_id, CACHE_TENANT)


class WhenTestingTokenCache(unittest.TestCase):

    def setUp(self):
        self.cache_clear = MagicMock()
        self.cache_true = MagicMock(return_value=True)
        self.cache_false = MagicMock(return_value=False)
        self.cache_update = MagicMock()
        self.cache_set = MagicMock()
        self.cache_del = MagicMock()
        self.tenant_id = '101'
        self.token = Token()
        self.token_json = jsonutils.dumps(self.token.format())
        self.cache_get_token = MagicMock(return_value=self.token_json)

    def test_clear_calls_cache_clear(self):
        with patch.object(NativeProxy, 'cache_clear', self.cache_clear):
            token_cache = TokenCache()
            token_cache.clear()
        self.cache_clear.assert_called_once_with(CACHE_TOKEN)

    def test_set_token_calls_cache_update(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_true
        ), patch.object(NativeProxy, 'cache_update', self.cache_update):
            token_cache = TokenCache()
            token_cache.set_token(self.tenant_id, self.token)

        self.cache_update.assert_called_once_with(
            self.tenant_id, jsonutils.dumps(self.token.format()),
            DEFAULT_EXPIRES, CACHE_TOKEN)

    def test_set_token_calls_cache_set(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_false
        ), patch.object(NativeProxy, 'cache_set', self.cache_set):
            token_cache = TokenCache()
            token_cache.set_token(self.tenant_id, self.token)

        self.cache_set.assert_called_once_with(
            self.tenant_id, jsonutils.dumps(self.token.format()),
            DEFAULT_EXPIRES, CACHE_TOKEN)

    def test_get_token_calls_returns_tenant(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_true
        ), patch.object(NativeProxy, 'cache_get',  self.cache_get_token):
            token_cache = TokenCache()
            token = token_cache.get_token(self.tenant_id)

        self.cache_get_token.assert_called_once_with(
            self.tenant_id, CACHE_TOKEN)
        self.assertIsInstance(token, Token)

    def test_get_token_calls_returns_none(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_false):
            token_cache = TokenCache()
            token = token_cache.get_token(self.tenant_id)

        self.assertIs(token, None)

    def test_delete_token_calls_cache_del(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_true
        ), patch.object(NativeProxy, 'cache_del', self.cache_del):
            token_cache = TokenCache()
            token_cache.delete_token(self.tenant_id)

        self.cache_del.assert_called_once_with(
            self.tenant_id, CACHE_TOKEN)

    def test_delete_token_does_not_call_cache_del(self):
        with patch.object(
                NativeProxy, 'cache_exists', self.cache_false
        ), patch.object(NativeProxy, 'cache_del', self.cache_del):
            token_cache = TokenCache()
            token_cache.delete_token(self.tenant_id)

        with self.assertRaises(AssertionError):
            self.cache_del.assert_called_once_with(
                self.tenant_id, CACHE_TOKEN)


if __name__ == '__main__':
    unittest.main()
