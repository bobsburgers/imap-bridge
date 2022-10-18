def get_body_bounce(msg, contact_email=None):
    return parse(msg.plaintext, contact_email)


def parse(body, known_email):
    result = {'email': '',
              'bounce_type': False,
              'remove': 0,
              'rule_cat': None,
              'rule_no': '0000'
              }
