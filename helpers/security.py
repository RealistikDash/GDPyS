# This helper is used for verifying some of the post
# args sent by some endpoints. To keep the handlers
# clean, these will be kept here. 

def verify_stats_seed(seed: str) -> bool:
    """Verifies if the seed sent in the `seed` post
    argument of the request is valid by performing
    several checks on it.
    
    Args:
        seed (str): The seed passed by Geometry Dash
            as part of the request.
    
    Returns:
        True if valid, else False.
    """

    # Currently, all I know is that this is a completely
    # random string that's 10 chars long.
    if len(seed) != 10 or seed.isnumeric():
        return False
    
    # All checks passed.
    return True
