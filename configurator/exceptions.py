# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.




class AlreadyProcessed(Exception):
    """
    An exception raised when an attempt is made to strictly
    :meth:`~configurator._api.API.process` a
    :class:`~configurator.section.Section` that has already
    been processed.
    """
