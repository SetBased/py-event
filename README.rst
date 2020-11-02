py-event
========

A single threaded and a run-to-completion event controller. That is, each event is processed completely before any other event is processed. Hence, an event listener will run entirely before any other code runs (which can potentially modify the data the event listener invokes).

License
=======

This project is licensed under the terms of the MIT license.
