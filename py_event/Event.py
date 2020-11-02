import weakref
from _weakref import ReferenceType
from typing import Any


class Event:
    """
    Class for events.
    """

    # ------------------------------------------------------------------------------------------------------------------
    event_controller = None
    """
    The event controller.

    :type: None|py_event.EventController.EventController
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, source: Any):
        """
        Object constructor.

        :param Any source: The object that emits this event.
        """

        self._source = source
        """
        The object that generates this event.

        :type: py_event.EventActor.EventActor
        """

        self.ref: ReferenceType = weakref.ref(self, Event.event_controller.internal_unregister_event_ref)
        """
        The weak reference to this event.
        """

        # Register this event as an event in the current program.
        Event.event_controller.internal_register_event(self)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def source(self) -> Any:
        """
        Returns the object that fires this event.
        """
        return self._source

    # ------------------------------------------------------------------------------------------------------------------
    def fire(self, event_data: Any = None) -> None:
        """
        Fires this event. That is, the event is put on the event queue of the event controller.

        Normally this method is called by the source of this event.

        :param Any event_data: Additional data supplied by the event source.
        """
        Event.event_controller.internal_queue_event(self, event_data)

    # ------------------------------------------------------------------------------------------------------------------
    def register_listener(self, listener: callable, listener_data: Any = None) -> None:
        """
        Registers a callable as a listener for this event.

        :param callable listener: Will be called when this events fires.
        :param Any listener_data: Additional data supplied by the listener destination.
        """
        Event.event_controller.internal_register_listener(self, listener, listener_data)

# ----------------------------------------------------------------------------------------------------------------------
