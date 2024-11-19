import os
import pytest
import contextlib
from pytest_client_tools.util import Version
import conftest
from constants import RHSM, RHSM_REGISTER_SERVER, RHSM_REGISTER
from dasbus.connection import SystemMessageBus, MessageBus
import sh
import subprocess
from dasbus.client.observer import DBusObserver, DBusObserverError

import gi
gi.require_version("Gio", "2.0")
from gi.repository import Gio
import logging

log = logging.getLogger(__name__)

"""
It is important to run tests as root. Since RegisterServer is a system dbus service.
And it provides a unix socket connection.
"""

class RHSMPrivateBus(MessageBus):
    """Representation of RHSM private bus connection that can be used as a context manager."""

    def __init__(self, rhsm_register_server_proxy, *args, **kwargs):
        """Representation of RHSM private bus connection that can be used as a context manager.

        :param rhsm_register_server_proxy: DBus proxy for the RHSM RegisterServer object
        """
        super().__init__(*args, **kwargs)
        self._rhsm_register_server_proxy = rhsm_register_server_proxy
        self._private_bus_address = None

    def __enter__(self):
        log.debug("subscription: starting RHSM private DBus session")
        locale = os.environ.get("LANG", "")
        self._private_bus_address = self._rhsm_register_server_proxy.Start(locale)
        log.debug("subscription: RHSM private DBus session has been started")
        return self

    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        log.debug("subscription: shutting down the RHSM private DBus session")
        self.disconnect()
        locale = os.environ.get("LANG", "")
        self._rhsm_register_server_proxy.Stop(locale)
        log.debug("subscription: RHSM private DBus session has been shutdown")

    def _get_connection(self):
        """Get a connection to RHSM private DBus session."""
        # the RHSM private bus address is potentially sensitive
        # so we will not log it
        log.info("Connecting to the RHSM private DBus session.")
        return self._provider.get_addressed_bus_connection(
            bus_address=self._private_bus_address,
            flags=Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT
        )

def test_start_register_server(test_config):
    """
        dbus-send --system --print-reply --dest='com.redhat.RHSM1' \
            '/com/redhat/RHSM1/RegisterServer' \
            com.redhat.RHSM1.RegisterServer.Start string:"" > /root/register_server_output.txt

    if [[ $? -eq 0 ]]
    then
        export my_addr=`cat /root/register_server_output.txt | gawk '/string/{ print $2 }' | sed 's/\"//g'`
        echo "Using address: $my_addr"
    else
        echo "Unable to start RegisterServer"
    fi
    """
    # result = subprocess.run(" ".join(["dbus-send",
    #                                  "--system",
    #                                  "--print-reply",
    #                                  "--dest='com.redhat.RHSM1'",
    #                                  '/com/redhat/RHSM1/RegisterServer',
    #                                  "com.redhat.RHSM1.RegisterServer.Start",
    #                                   'string:""']),
    #                         shell=True,
    #                         capture_output=True)
    # print(result)
    print("ahoj")
    print(type(RHSM))
    print(RHSM.service_name)
    # bus=SystemMessageBus()
    # object_path=RHSM._choose_object_path(RHSM_REGISTER_SERVER)
    # interface_name=RHSM._choose_interface_name(RHSM_REGISTER_SERVER)
    # bus.get_proxy(RHSM.service_name,object_path, interface_name)
                               
    proxy = RHSM.get_proxy(RHSM_REGISTER_SERVER)
    print(proxy)
    with RHSMPrivateBus(proxy) as private_bus:
        private_proxy = private_bus.get_proxy(RHSM.service_name,
                                              RHSM_REGISTER.object_path)
        print(private_proxy)
        try:
            locale = os.environ.get("LANG", "")
            private_proxy.Register(test_config.get("organization"),
                                   test_config.get("username"),
                                   test_config.get("password"),
                                   {},
                                   {},
                                   locale)
        except DBusError as e:
            log.debug("subscription: failed to register with username and password: %s",
                      str(e))
            # RHSM exception contain details as JSON due to DBus exception handling limitations
            exception_dict = json.loads(str(e))
            # return a generic error message in case the RHSM provided error message is missing
            message = exception_dict.get("message", _("Registration failed."))
            raise RegistrationError(message) from None

        
def test_register():
    """
    https://www.candlepinproject.org/docs/subscription-manager/dbus_objects.html#methods-6
    """

