.. currentmodule:: tixte

API Reference
=============

Client
------

.. attributetable:: Client

.. autoclass:: Client
    :members:
    :exclude-members: dispatch

    .. automethod:: Client.event()
        :decorator:

ABC
---

Object
~~~~~~~

.. attributetable:: tixte.abc.Object

.. autoclass:: tixte.abc.Object
    :members:

IDable
~~~~~~

.. attributetable:: tixte.abc.IDable

.. autoclass:: tixte.abc.IDable
    :members:

Objects
-------

Configuration
~~~~~~~~~~~~~

.. attributetable:: Config

.. autoclass:: Config
    :members:

Domain
~~~~~~

.. attributetable:: Domain

.. autoclass:: Domain
    :members:

File 
~~~~

.. attributetable:: File

.. autoclass:: File
    :members:

PartialUpload
~~~~~~~~~~~~~

.. attributetable:: PartialUpload

.. autoclass:: PartialUpload
    :members:

Upload
~~~~~~

.. attributetable:: Upload

.. autoclass:: Upload
    :members:

DeleteResponse
~~~~~~~~~~~~~~

.. attributetable:: DeleteResponse

.. autoclass:: DeleteResponse
    :members:

Users
-----

User
~~~~

.. attributetable:: User

.. autoclass:: User
    :members:

ClientUser
~~~~~~~~~~

.. attributetable:: ClientUser

.. autoclass:: ClientUser
    :members:
    :inherited-members:

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