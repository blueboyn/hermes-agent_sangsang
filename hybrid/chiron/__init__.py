"""Chiron — a hybrid self-evolution engine.

Chiron fuses two complementary approaches to machine self-evolution:

  * **agi / 상상이** grows *declarative knowledge*: it detects gaps, acquires
    knowledge, and discovers novel causal connections in a graph.
  * **hermes** grows *procedural skill*: it captures "how to do a class of
    task" as reusable, consolidated, recoverable artifacts.

The fusion thesis (see ARCHITECTURE.md): let knowledge grow freely, but gate
every new fact through validation, and *promote* only validated, recurring
knowledge into procedural skills. Nothing is ever deleted — only archived —
and every write carries provenance.
"""

from .config import Config
from .store import Store
from .orchestrator import Orchestrator

__all__ = ["Config", "Store", "Orchestrator"]
__version__ = "0.1.0"
