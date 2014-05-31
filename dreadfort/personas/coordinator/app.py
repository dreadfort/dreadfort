from multiprocessing import Process

import falcon

from dreadfort.api.status.resources import (
    WorkerStatusResource, WorkersStatusResource)
from dreadfort.api.tenant.resources import (
    EventProducerResource, EventProducersResource,
    UserResource, TenantResource, TokenResource)
from dreadfort.api.version.resources import VersionResource
from dreadfort import env
from dreadfort.queue import celery


_LOG = env.get_logger(__name__)


def start_up():
    # Common Resource(s)
    versions = VersionResource()

    # Coordinator Resources
    workers_status = WorkersStatusResource()
    worker_status = WorkerStatusResource()

    # Tenant Resources
    tenant = TenantResource()
    user = UserResource()
    event_producers = EventProducersResource()
    event_producer = EventProducerResource()
    token = TokenResource()

    # Create API
    application = api = falcon.API()

    # Common Routing
    api.add_route('/', versions)

    api.add_route('/v1/worker/{hostname}/status', worker_status)
    api.add_route('/v1/status', workers_status)

    # Tenant Routing
    api.add_route('/v1/tenant', tenant)
    api.add_route('/v1/tenant/{tenant_id}', user)
    api.add_route('/v1/tenant/{tenant_id}/producers', event_producers)
    api.add_route('/v1/tenant/{tenant_id}/producers/{event_producer_id}',
                  event_producer)

    api.add_route('/v1/tenant/{tenant_id}/token', token)

    celery_proc = Process(target=celery.worker_main)
    celery_proc.start()
    _LOG.info(
        'Celery started as process: {}'.format(celery_proc.pid)
    )

    return application
