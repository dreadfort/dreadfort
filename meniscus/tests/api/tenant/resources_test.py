from meniscus.api.tenant.resources import *
from meniscus.model.tenant import Tenant, Host, HostProfile

from mock import MagicMock
from mock import patch

import falcon
import unittest


def suite():
    suite = unittest.TestSuite()
    suite.addTest(WhenTestingVersionResource())

    return suite


class WhenTestingVersionResource(unittest.TestCase):

    def setUp(self):
        self.req = MagicMock()
        self.resp = MagicMock()
        self.resource = VersionResource()

    def test_should_return_200_on_get(self):
        self.resource.on_get(self.req, self.resp)
        self.assertEqual(falcon.HTTP_200, self.resp.status)

    def test_should_return_version_json(self):
        self.resource.on_get(self.req, self.resp)

        parsed_body = json.loads(self.resp.body)

        self.assertTrue('v1' in parsed_body)
        self.assertEqual('current', parsed_body['v1'])


class WhenTestingTenantResource(unittest.TestCase):

    def setUp(self):
        db_filter = MagicMock()
        db_filter.one.return_value = Tenant('tenant_id')

        db_query = MagicMock()
        db_query.filter_by.return_value = db_filter

        self.db_session = MagicMock()
        self.db_session.query.return_value = db_query

        self.stream = MagicMock()
        self.stream.read.return_value = u'{ "tenant_id" : "1234" }'

        self.req = MagicMock()
        self.req.stream = self.stream

        self.resp = MagicMock()
        self.resource = TenantResource(self.db_session)

        self.tenant_not_found = MagicMock(return_value=None)
        self.tenant_found = MagicMock(return_value=Tenant('1234'))

    def test_should_throw_exception_for_tenants_that_exist_on_post(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_found):
            with self.assertRaises(falcon.HTTPError):
                self.resource.on_post(self.req, self.resp)

    def test_should_return_201_on_post(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_not_found):
            self.resource.on_post(self.req, self.resp)

        self.assertEquals(falcon.HTTP_201, self.resp.status)


class WhenTestingUserResource(unittest.TestCase):

    def setUp(self):
        db_filter = MagicMock()
        db_filter.one.return_value = Tenant('tenant_id')

        db_query = MagicMock()
        db_query.filter_by.return_value = db_filter

        self.db_session = MagicMock()
        self.db_session.query.return_value = db_query

        self.stream = MagicMock()

        self.req = MagicMock()
        self.req.stream = self.stream

        self.resp = MagicMock()
        self.resource = UserResource(self.db_session)

        self.tenant_id = '1234'
        self.tenant_not_found = MagicMock(return_value=None)
        self.tenant_found = MagicMock(return_value=Tenant(self.tenant_id))

    def test_should_throw_exception_for_tenants_not_found_on_get(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_not_found):
            with self.assertRaises(falcon.HTTPError):
                self.resource.on_get(self.req, self.resp, self.tenant_id)

    def test_should_return_200_on_get(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_found):
            self.resource.on_get(self.req, self.resp, self.tenant_id)
        self.assertEquals(falcon.HTTP_200, self.resp.status)

    def test_should_return_tenant_json_on_get(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_found):
            self.resource.on_get(self.req, self.resp, self.tenant_id)

        parsed_body = json.loads(self.resp.body)

        self.assertTrue('tenant' in parsed_body)
        self.assertTrue('tenant_id' in parsed_body['tenant'])
        self.assertEqual(self.tenant_id, parsed_body['tenant']['tenant_id'])

    def test_should_throw_exception_for_tenants_not_found_on_delete(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_not_found):
            with self.assertRaises(falcon.HTTPError):
                self.resource.on_delete(self.req, self.resp, self.tenant_id)

    def test_should_return_200_on_delete(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_found):
            self.resource.on_delete(self.req, self.resp, self.tenant_id)
        self.assertEquals(falcon.HTTP_200, self.resp.status)


class WhenTestingHostProfilesResource(unittest.TestCase):

    def setUp(self):
        db_filter = MagicMock()
        db_filter.one.return_value = Tenant('tenant_id')

        db_query = MagicMock()
        db_query.filter_by.return_value = db_filter

        self.db_session = MagicMock()
        self.db_session.query.return_value = db_query

        self.stream = MagicMock()

        self.req = MagicMock()
        self.req.stream = self.stream

        self.resp = MagicMock()
        self.resource = HostProfilesResource(self.db_session)

        self.profiles = [HostProfile(123, 'profile1'),
                         HostProfile(456, 'profile2')]

        self.producers = [EventProducer(432, 'producer1', 'syslog')]

        self.tenant_id = '1234'
        self.tenant_not_found = MagicMock(return_value=None)
        self.tenant_found = MagicMock(
            return_value=Tenant(self.tenant_id, profiles=self.profiles,
                                event_producers=self.producers))

    def test_should_throw_exception_for_tenants_not_found_on_get(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_not_found):
            with self.assertRaises(falcon.HTTPError):
                self.resource.on_get(self.req, self.resp, self.tenant_id)

    def test_should_return_200_on_get(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_found):
            self.resource.on_get(self.req, self.resp, self.tenant_id)
        self.assertEquals(falcon.HTTP_200, self.resp.status)

    def test_should_return_profiles_json_on_get(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_found):
            self.resource.on_get(self.req, self.resp, self.tenant_id)

        parsed_body = json.loads(self.resp.body)

        self.assertEqual(len(self.profiles), len(parsed_body))

        for profile in parsed_body:
            self.assertTrue('id' in profile.keys())
            self.assertTrue('name' in profile.keys())
            self.assertTrue('event_producers' in profile.keys())

    def test_should_throw_exception_for_tenants_not_found_on_post(self):
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_not_found):
            with self.assertRaises(falcon.HTTPError):
                self.resource.on_post(self.req, self.resp, self.tenant_id)

    def test_should_throw_exception_for_profile_found_on_post(self):
        self.stream.read.return_value = u'{ "name" : "profile1" }'
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_found):
            with self.assertRaises(falcon.HTTPError):
                self.resource.on_post(self.req, self.resp, self.tenant_id)

    def test_should_throw_exception_for_producer_not_found_on_post(self):
        self.stream.read.return_value = \
            u'{ "name" : "profile99", "event_producer_ids":[1,2]}'
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_found):
            with self.assertRaises(falcon.HTTPError):
                self.resource.on_post(self.req, self.resp, self.tenant_id)

    def test_should_return_201_on_post_no_event_producers(self):
        self.stream.read.return_value = \
            u'{ "name" : "profile99", "event_producer_ids":[]}'
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_found):
            self.resource.on_post(self.req, self.resp, self.tenant_id)
        self.assertEquals(falcon.HTTP_201, self.resp.status)

    def test_should_return_201_on_post_with_event_producers(self):
        self.stream.read.return_value = \
            u'{ "name" : "profile99", "event_producer_ids":[432]}'
        with patch('meniscus.api.tenant.resources.find_tenant',
                   self.tenant_found):
            self.resource.on_post(self.req, self.resp, self.tenant_id)
        self.assertEquals(falcon.HTTP_201, self.resp.status)

if __name__ == '__main__':
    unittest.main()