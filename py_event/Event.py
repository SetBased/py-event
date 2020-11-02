import weakref
from _weakref import ReferenceType
from typing import Any, Dict, List, Tuple


class Event:
    """
    Class for events.

    Methods with name starting with 'internal_' MUST not be called from your application (only friend classes are
    allowed to call these methods).
    """

    # ------------------------------------------------------------------------------------------------------------------
    __event_dispatcher = None
    """
    The event dispatcher.

    :type: None|py_event.EventDispatcher.EventDispatcher
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, emitter: Any):
        """
        Object constructor.

        :param Any emitter: The object that emits this event.
        """

        self.__emitter: Any = emitter
        """
        The object that emits this event.
        """

        self.__listeners: Dict[ReferenceType, List[Tuple[callable, Any]]] = {}
        """
        The listeners that will be notified when this events has been triggered.        
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def emitter(self) -> Any:
        """
        Returns the object that emits this event.
        """
        return self.__emitter

    # ------------------------------------------------------------------------------------------------------------------
    def trigger(self, event_data: Any = None) -> None:
        """
        Triggers this event. That is, the event is put on the event queue of the event dispatcher.

        Normally this method is called by the emitter of this event.

        :param Any event_data: Additional data supplied by the event emitter.
        """
        Event.__event_dispatcher.internal_queue_event(self, event_data)

    # ------------------------------------------------------------------------------------------------------------------
    def unregister_object(self, instance: Any) -> None:
        """
        Unregisters all methods that are listeners of this event as listeners.

        :param Any instance: An object.
        """
        listener_ref = weakref.ref(instance)
        if listener_ref in self.__listeners:
            del self.__listeners[listener_ref]

    # ------------------------------------------------------------------------------------------------------------------
    def unregister_method(self, method: callable) -> None:
        """
        Unregisters a method as listener of this event.

        :param Any method: The listener.
        """
        if hasattr(method, '__self__'):
            listener_ref = weakref.ref(method.__self__)
            if listener_ref in self.__listeners:
                listeners = self.__listeners[listener_ref]
                for key in range(len(listeners) - 1, -1, -1):
                    if listeners[key][0] == method.__func__:
                        del listeners[key]

                if not listeners:
                    del self.__listeners[listener_ref]

    # ------------------------------------------------------------------------------------------------------------------
    def register_listener(self, method: callable, listener_data: Any = None) -> None:
        """
        Registers a listener for this event.

        :param callable method: Will be called when this event has been triggered.
        :param Any listener_data: Additional data supplied by the listener destination.
        """
        if not hasattr(method, '__self__'):
            raise ValueError('Only an object can be a listener')

        listener_ref = weakref.ref(method.__self__, self.internal_unregister_listener)
        if listener_ref not in self.__listeners:
            self.__listeners[listener_ref] = []

        self.__listeners[listener_ref].append((method.__func__, listener_data))

    # ------------------------------------------------------------------------------------------------------------------
    def internal_unregister_listener(self, listener_ref: ReferenceType) -> None:
        """
        Unregisters a listener for this event.

        :param ReferenceType listener_ref: The weak references to the listener.
        """
        del self.__listeners[listener_ref]

    # ------------------------------------------------------------------------------------------------------------------
    def internal_get_listeners(self) -> Dict[ReferenceType, List[Tuple[callable, Any]]]:
        """
        Returns all listeners of this event.
        """
        return self.__listeners

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def internal_set_dispatcher(dispatcher) -> None:
        """
        Sets the event dispatcher.

        :param py_event.EventDispatcher.EventDispatcher dispatcher: The event dispatcher.
        """
        Event.__event_dispatcher = dispatcher

# ----------------------------------------------------------------------------------------------------------------------
