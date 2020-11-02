import weakref
from _weakref import ReferenceType

from py_event.Event import Event


class EventActor:
    """
    Parent class for classes that fire events and for classes that listen for events.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Object constructor.
        """

        self.ref: ReferenceType = weakref.ref(self, Event.event_controller.internal_unregister_listener_object_ref)
        """
        The weak reference to this event actor.
        """

# ----------------------------------------------------------------------------------------------------------------------
