from os import environ
from oslo.config import cfg
from dreadfort.openstack.common import log
from dreadfort.config import _DEFAULT_CONFIG_ARGS


CONF = cfg.CONF
CONF.import_opt('verbose', 'dreadfort.openstack.common.log')
CONF.import_opt('debug', 'dreadfort.openstack.common.log')
CONF.import_opt('log_file', 'dreadfort.openstack.common.log')
CONF.import_opt('log_dir', 'dreadfort.openstack.common.log')
CONF.import_opt('use_syslog', 'dreadfort.openstack.common.log')
CONF.import_opt('syslog_log_facility', 'dreadfort.openstack.common.log')
CONF.import_opt('log_config', 'dreadfort.openstack.common.log')

try:
    cfg.CONF(args=_DEFAULT_CONFIG_ARGS)
except cfg.ConfigFilesNotFoundError as ex:
    pass


def get_logger(logger_name):
    return log.getLogger(logger_name)


def get(name, default=None):
    value = environ.get(name)
    return value if value else default
