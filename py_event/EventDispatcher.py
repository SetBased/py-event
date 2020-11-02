import traceback
from typing import Any, List, Tuple

from py_event.Event import Event


class EventDispatcher:
    """
    A single threaded and a run-to-completion event dispatcher. That is, each event is processed completely before any
    other event is processed. Hence, an event listener will run entirely before any other code runs (which can
    potentially modify the data the event listener invokes).

    Methods with name starting with 'internal_' MUST not be called from your application (only friend classes are
    allowed to call these methods).
    """
    # ------------------------------------------------------------------------------------------------------------------
    __instance = None
    """
    The singleton instance of this class.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Object constructor.
        """
        if EventDispatcher.__instance:
            raise RuntimeError('Can only create one instance of {}'.format(self.__class__))

        self.__event_loop_start: Event = Event(self)
        """
        Event that will be triggered at the start of the event loop.
        """

        self.__event_loop_end: Event = Event(self)
        """
        Event that will be triggered at the end of the event loop.
        """

        self.__event_queue_empty = Event(self)
        """
        Event that will be triggered when the event queue is empty.
        """

        self.__queue: List[Tuple[Event, Any]] = []
        """
        The queue with events that have been triggered but have not been dispatched yet.
        """

        self.__is_running: bool = False
        """
        True if and only if this dispatcher is dispatching events.
        """

        self.exit: bool = False
        """
        If True the event loop terminates as soon as the event queue is emtpy.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __del__(self):
        """
        Object destructor.
        """
        EventDispatcher.__instance = None

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def instance():
        """
        Returns the singleton instance of the event dispatcher.

        :rtype: EventDispatcher
        """
        if not EventDispatcher.__instance:
            EventDispatcher.__instance = EventDispatcher()
            Event.internal_set_dispatcher(EventDispatcher.__instance)

        return EventDispatcher.__instance

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def event_loop_end(self) -> Event:
        """
        Returns the event that will be triggered at the end of the event loop.
        """
        return self.__event_loop_end

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def event_loop_start(self) -> Event:
        """
        Returns the event that will be triggered at the start of the event loop.
        """
        return self.__event_loop_start

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def event_queue_empty(self) -> Event:
        """
        Returns the event that will be triggered when the event queue is empty.
        """
        return self.__event_queue_empty

    # ------------------------------------------------------------------------------------------------------------------
    def queue_size(self) -> int:
        """
        Returns the number of event on the event queue.
        """
        return len(self.__queue)

    # ------------------------------------------------------------------------------------------------------------------
    def loop(self) -> None:
        """
        Start the event handler loop.

        The event handler loop terminates under each of the conditions below:
        * The event handler for 'event_queue_empty' completes without adding new events on the event queue.
        * Property exit has been set to True and the event queue is empty. Note: after property exit has been set to
          True event 'event_queue_empty' will not be triggered.
        """
        self.__dispatch_event(self.__event_loop_start, None)

        if not self.exit and not self.__queue:
            self.__dispatch_event(self.__event_queue_empty, None)

        while self.__queue:
            event, event_data = self.__queue.pop(0)

            self.__dispatch_event(event, event_data)

            if not self.__queue and not self.exit:
                self.__dispatch_event(self.__event_queue_empty, None)
                if not self.__queue:
                    self.exit = True

        self.__dispatch_event(self.__event_loop_end, None)

    # ------------------------------------------------------------------------------------------------------------------
    def __dispatch_event(self, event: Event, event_data: Any) -> None:
        """
        Dispatches an event.

        :param Event event: The event to be dispatch.
        :param Any event_data: Additional data supplied by the event emitter.
        """
        listeners = event.internal_get_listeners()
        for listener_ref in listeners:
            listener_object = listener_ref()
            if listener_object:
                for function, listener_data in listeners[listener_ref]:
                    try:
                        function(listener_object, event, event_data, listener_data)
                    except Exception:
                        traceback.print_exc()

    # ------------------------------------------------------------------------------------------------------------------
    def internal_queue_event(self, event: Event, event_data: Any) -> None:
        """
        Puts an event that has been triggered on the event queue.

        Note: Do not use this method directly. Use py_event.Event.Event.trigger() instead.

        :param Event event: The event that has been triggered.
        :param Any event_data: Additional data supplied by the event emitter.
        """
        self.__queue.append((event, event_data))

# ----------------------------------------------------------------------------------------------------------------------
