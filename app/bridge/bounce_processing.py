from app.bridge.body_parser import get_body_bounce
from app.bridge.dsn_parser import get_dsn_bounce


def check_if_bounce(msg):
    bouncerAddress = None
    for to, name in msg.message.to.items():
        # Some ISPs strip the + email so will still process the content for a bounce
        # even if a +bounce address was not found
        if '+bounce' in to:
            bouncerAddress = to
            break
    try:
        # First parse for a DSN report
        bounce = get_dsn_bounce(msg)
    except Exception as exception:
        # todo this exception is to generic
        # DSN report wasn't found so try parsing the body itself
        # todo track down second value
        bounce = get_body_bounce(msg)
    
    if bouncerAddress:
        bounce['bounceAddress'] = bouncerAddress
    return bounce
