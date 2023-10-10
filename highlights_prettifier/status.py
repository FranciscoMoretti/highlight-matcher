from enum import Enum


class Status(Enum):
    ENABLED = 1  # Nodes that are currently enabled or active.
    DISABLED = 2  # Nodes that are currently disabled or inactive.
    TO_BE_REMOVED = (
        3  # Nodes that are marked for removal but have not been removed yet.
    )
    REMOVED = 4  # Nodes that have been removed and should not be considered in the list anymore.
    NO_STATUS = 5  # Some nodes can't hold a status
