from oslo.config import cfg

import dreadfort.config as config
from dreadfort import env
from dreadfort.sinks import elasticsearch

_LOG = env.get_logger(__name__)

_DATA_SINKS_GROUP = cfg.OptGroup(name='data_sinks', title='Data Sink List')
config.get_config().register_group(_DATA_SINKS_GROUP)

_SINK = [
    cfg.ListOpt('valid_sinks',
                default=['elasticsearch'],
                help="""valid data sinks list"""
                ),
    cfg.StrOpt('default_sink',
               default='elasticsearch',
               help="""default data sink"""
               )
]

config.get_config().register_opts(_SINK, group=_DATA_SINKS_GROUP)

try:
    config.init_config()
except config.cfg.ConfigFilesNotFoundError as ex:
    _LOG.exception(ex.message)

conf = config.get_config()

VALID_SINKS = conf.data_sinks.valid_sinks
DEFAULT_SINK = conf.data_sinks.default_sink


def route_message(message):
    message_sinks = message['dreadfort']['correlation']['sinks']
    if 'elasticsearch' in message_sinks:
        elasticsearch.put_message.delay(message)
