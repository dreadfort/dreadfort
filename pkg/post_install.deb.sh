#!/bin/sh
# postinst script for dreadfort
#
# see: dh_installdeb(1)

set -e

# summary of how this script can be called:
#        * <postinst> `configure' <most-recently-configured-version>
#        * <old-postinst> `abort-upgrade' <new version>
#        * <conflictor's-postinst> `abort-remove' `in-favour' <package>
#          <new-version>
#        * <postinst> `abort-remove'
#        * <deconfigured's-postinst> `abort-deconfigure' `in-favour'
#          <failed-install-package> <version> `removing'
#          <conflicting-package> <version>
# for details, see http://www.debian.org/doc/debian-policy/ or
# the debian-policy package


case "$1" in
    configure)
	    . /usr/share/debconf/confmodule

	    if ! (getent group dreadfort) > /dev/null 2>&1; then
	        addgroup --quiet --system dreadfort > /dev/null
		fi

		if ! (getent passwd dreadfort) > /dev/null 2>&1; then
		    adduser --quiet --system --home /var/lib/dreadfort --ingroup dreadfort --no-create-home --shell /bin/false dreadfort
		fi

        chown root:root /etc/init/dreadfort.conf
        chown -R root:root /usr/share/dreadfort
        chmod -R 0755 /usr/share/dreadfort

		if [ ! -d /var/log/dreadfort ]; then
            mkdir /var/log/dreadfort
            chown -R dreadfort:adm /var/log/dreadfort/
            chmod 0755 /var/log/dreadfort/
        fi

        if [ ! -d /var/lib/dreadfort ]; then
            mkdir /var/lib/dreadfort
            chown dreadfort:dreadfort -R /var/lib/dreadfort/ /etc/dreadfort
            chmod -R 0755 /etc/dreadfort/
        fi
    ;;

    abort-upgrade|abort-remove|abort-deconfigure)
    ;;

    *)
        echo "postinst called with unknown argument \`$1'" >&2
        exit 1
    ;;
esac

# dh_installdeb will replace this with shell code automatically
# generated by other debhelper scripts.

#DEBHELPER#

exit 0
