.. currentmodule:: tixte

API Reference
=============

Client
------

.. attributetable:: Client

.. autoclass:: Client
    :members:
    :exclude-members: dispatch, listen

    .. automethod:: Client.listen()
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

Config
~~~~~~

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
    :inherited-members:

DeleteResponse
~~~~~~~~~~~~~~

.. attributetable:: DeleteResponse

.. autoclass:: DeleteResponse
    :members:

Permissions
~~~~~~~~~~~

.. attributetable:: Permissions

.. autoclass:: Permissions
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

Enums
-----

Region
~~~~~~

.. class:: Region
    
    Represents an upload region.

    .. attribute:: us_east_one

        Represents the US East region.
    
Premium
~~~~~~~

.. class:: Premium
    
    Represents the premium tiers of Tixte.

    .. attribute:: free

        The free tier. All default members have this tier.
    
    .. attribute:: turbo

        Turbo tier. All members with this tier have an increased upload limit.
    
    .. attribute:: turbo_charged

        Turbo charged tier. This is the highest tier. All members with this tier have an increased upload limit.
    

UploadPermissionLevel
~~~~~~~~~~~~~~~~~~~~~

.. class:: UploadPermissionLevel

    Represents an upload permission level. This level determines
    which members can view an upload.

    .. attribute:: viewer
        
        A viewer of this upload.
    
    .. attribute:: manager

        A manager of this upload. Can manage viewers.
    
    .. attribute:: owner
        
        The owner of this upload. Can manage everything.

UploadType
~~~~~~~~~~~~~~

.. class:: UploadType

    Represents the type of file being uploaded.

    .. attribute:: public

        A public file. Anyone can view this file.
    
    .. attribute:: private

        A private file. Only the owner can view this file.
        

.. _tixte-api-utils:

Utility Functions
-----------------

.. autofunction:: tixte.utils.parse_time

Event Reference
----------------

Events
~~~~~~
.. function:: on_request(response)

    A listener that gets dispatched everytime a request is made from the library.

    :param aiohttp.ClientResponse response: The response from the server when making a HTTP request.

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

.. autoexception:: PaymentRequired
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
              - :exc:`PaymentRequired`