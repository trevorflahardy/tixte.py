.. currentmodule:: tixte

API Reference
=============

Client
------

Client
~~~~~~

.. autoclass:: Client
    :members:
    :exclude-members: dispatch

    .. automethod:: Client.event()
        :decorator:

ABC
---

Object
~~~~~~~

.. autoclass:: tixte.abc.Object
    :members:

IDable
~~~~~~

.. autoclass:: tixte.abc.IDable
    :members:

Objects
-------

Configuration
~~~~~~~~~~~~~

.. autoclass:: Config
    :members:

Domain
~~~~~~

.. autoclass:: Domain
    :members:

File 
~~~~

.. autoclass:: File
    :members:

PartialUpload
~~~~~~~~~~~~~

.. autoclass:: PartialUpload
    :members:

Upload
~~~~~~

.. autoclass:: Upload
    :members:

DeleteResponse
~~~~~~~~~~~~~~

.. autoclass:: DeleteResponse
    :members:

Users
-----

User
~~~~

.. autoclass:: User
    :members:

ClientUser
~~~~~~~~~~

.. autoclass:: ClientUser
    :members:

Exceptions
----------

Exceptions
~~~~~~~~~~

.. autoexception:: TixteException

.. autoexception:: HTTPException
    :members:

.. autoexception:: NotFound
    :members:

.. autoexception:: Forbidden
    :members:

.. autoexception:: TixteServerError
    :members:


Exception Hierarchy
~~~~~~~~~~~~~~~~~~~~~
                        
.. exception_hierarchy::

    - :exc:`Exception`
        - :exc:`TixteException`
           - :exc:`HTTPException`
              - :exc:`NotFound`
              - :exc:`Forbidden`
              - :exc:`TixteServerError`