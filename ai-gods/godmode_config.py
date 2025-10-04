# godmode_config.py

# This file centralizes the configuration for the Godmode AI system.
# By setting AUTONOMY_LEVEL to 'FULL', we grant all agents
# the permission to perform any action they deem necessary without
# requiring manual approval. This includes file modifications,
*# dependency installations, and task delegation.

AUTONOMY_LEVEL = "FULL"

def is_full_autonomy_enabled():
    """Check if the system is configured for full autonomy."""
    return AUTONOMY_LEVEL == "FULL"
