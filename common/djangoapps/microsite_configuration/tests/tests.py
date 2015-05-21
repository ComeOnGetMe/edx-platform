"""
Holds base classes for microsite tests
"""
from mock import DEFAULT

from django.test import TestCase
from microsite_configuration.tests.factories import (
    MicrositeFactory,
    MicrositeOrgMappingFactory,
)

MICROSITE_BACKENDS = (
    'microsite_configuration.backends.filebased.SettingsFileMicrositeBackend',
    'microsite_configuration.backends.database.DatabaseMicrositeBackend',
)


class DatabaseMicrositeTest(TestCase):
    """
    Base class for microsite related tests.
    """
    def setUp(self):
        super(DatabaseMicrositeTest, self).setUp()
        self.microsite = MicrositeFactory.create()
        MicrositeOrgMappingFactory.create(microsite=self.microsite, org='TestMicrositeX')


def side_effect_for_get_value(value, return_value):
    """
    returns a side_effect with given return value for a given value
    """
    def side_effect(*args, **kwargs):  # pylint: disable=unused-argument
        """
        A side effect for tests which returns a value based
        on a given argument otherwise return actual function.
        """
        if args[0] == value:
            return return_value
        else:
            return DEFAULT
    return side_effect
