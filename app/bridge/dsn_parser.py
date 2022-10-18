# This should check the dsn report provided by the email and determine if there is a recognized bounce.
import re

from app.bridge.catagories import category


def get_dsn_bounce(msg):
    dsn_message = msg.dsn_message or msg.plaintext
    dsn_report = msg.dsn_report
    return parse(dsn_message, dsn_report)


def parse(dsn_message, dsn_report):
    result = {'email': '',
              'bounce_type': False,
              'remove': 0,
              'rule_cat': None,
              'rule_no': '0000'
              }
    action = False
    diagnosisCode = ''
    
    result['email'] = re.search('/Original-Recipient: rfc822(.*)/i', dsn_report)
    result['email'] = result['email'] or re.search('/Final-Recipient:\s?rfc822(.*)/i', dsn_report)
    
    action = re.search('/Action: (.+)/i', dsn_report)
    if action:
        action = action.lower()
    
    diagnosisCode = re.search("/Diagnostic-Code:((?:[^\n]|\n[\t ])+)(?:\n[^\t ]|$)/is", dsn_report) or ''
    
    if not result['email']:
        
        #     /* email address is empty
        #              * rule: full
        #              * sample:   DSN Message only
        #              * User quota exceeded: SMTP <xxxxx@yourdomain.com>
        #              */
        result['email'] = re.search("/quota exceed.*<(\S+@\S+\w)>/is", dsn_message)
        if result['email']:
            result['rule_cat'] = 'Full'
            result['rule_no'] = '0161'
    else:
        # action could be one of them as RFC:1894
        # "failed" / "delayed" / "delivered" / "relayed" / "expanded"

        if (action == 'failed'):
            # rule: full
            # * sample:
            # * Diagnostic-Code: X-Postfix me.domain.com platform: said: 552 5.2.2 Over
            # *   quota (in reply to RCPT TO command)
            #
            
            if re.search('/over.*quota/is', diagnosisCode):
                result['rule_cat'] = category['FULL']
                result['rule_no'] = '0105'
            elif re.search('/exceed.*quota/is', diagnosisCode):
                result['rule_cat'] = category['FULL']
                result['rule_no'] = '0129'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*full/is', diagnosisCode)):
                result['rule_cat'] = category['FULL']
                result['rule_no'] = '0145'
            elif (re.search('/Insufficient system storage/is', diagnosisCode)):
                result['rule_cat'] = category['FULL']
                result['rule_no'] = '0134'
            elif (re.search('/File too large/is', diagnosisCode)):
                result['rule_cat'] = category['FULL']
                result['rule_no'] = '0192'
            elif (re.search('/larger than.*limit/is', diagnosisCode)):
                result['rule_cat'] = category['OVERSIZE']
                result['rule_no'] = '0146'
            elif (
                re.search('/(?:alias|account|recipient|address|email|mailbox|user)(.*)not(.*)list/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0103'
            elif (re.search('/user path no exist/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0106'
            elif (re.search('/Relay.*(?:denied|prohibited|disallowed)/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0108'
            elif (re.search('/no.*valid.*(?:alias|account|recipient|address|email|mailbox|user)/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0185'
            elif (re.search('/Invalid.*(?:alias|account|recipient|address|email|mailbox|user)/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0111'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*(?:disabled|discontinued)/is',
                            diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0114'
            elif (re.search("/user doesn't have.*account/is", diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0127'
            elif (re.search('/(?:unknown|illegal).*(?:alias|account|recipient|address|email|mailbox|user)/is',
                            diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0128'
            elif (re.search("/(?:alias|account|recipient|address|email|mailbox|user).*(?:un|not\\s+)available/is",
                            diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0122'
            elif (re.search('/no (?:alias|account|recipient|address|email|mailbox|user)/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0123'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*unknown/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0125'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*disabled/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0133'
            elif (re.search('/No such (?:alias|account|recipient|address|email|mailbox|user)/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0143'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*NOT FOUND/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0136'
            elif (re.search('/deactivated (?:alias|account|recipient|address|email|mailbox|user)/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0138'
            elif (re.search('/deactivated mailbox/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0138'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*reject/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0148'
            elif (re.search('/bounce.*administrator/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0151'
            elif (re.search('/<.*>.*disabled/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0152'
            elif (re.search('/not our customer/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0154'
            elif (re.search('/Wrong (?:alias|account|recipient|address|email|mailbox|user)/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0159'
            elif (
                re.search('/(?:unknown|bad).*(?:alias|account|recipient|address|email|mailbox|user)/is',
                          diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0160'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*not OK/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0186'
            elif (re.search('/Access.*Denied/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0189'
            elif (
                re.search('/(?:alias|account|recipient|address|email|mailbox|user).*lookup.*fail/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0195'
            elif (re.search('/(?:recipient|address|email|mailbox|user).*not.*member of domain/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0198'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*cannot be verified/is',
                            diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0202'
            elif (re.search('/Unable to relay/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0203'
            elif (re.search("/(?:alias|account|recipient|address|email|mailbox|user).*(?:n't|not).*exist/is",
                            diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0205'
            elif (re.search('/not have an account/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0207'
            elif (
                re.search('/(?:alias|account|recipient|address|email|mailbox|user).*is not allowed/is', diagnosisCode)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0220'
            elif (re.search('/inactive.*(?:alias|account|recipient|address|email|mailbox|user)/is', diagnosisCode)):
                result['rule_cat'] = category['INACTIVE']
                result['rule_no'] = '0135'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*Inactive/is', diagnosisCode)):
                result['rule_cat'] = category['INACTIVE']
                result['rule_no'] = '0155'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user) closed due to inactivity/is',
                            diagnosisCode)):
                result['rule_cat'] = category['INACTIVE']
                result['rule_no'] = '0170'
            elif (
                re.search('/(?:alias|account|recipient|address|email|mailbox|user) not activated/is', diagnosisCode)):
                result['rule_cat'] = category['INACTIVE']
                result['rule_no'] = '0177'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*(?:suspend|expire)/is',
                            diagnosisCode)):
                result['rule_cat'] = category['INACTIVE']
                result['rule_no'] = '0183'
            elif (
                re.search('/(?:alias|account|recipient|address|email|mailbox|user).*no longer exist/is',
                          diagnosisCode)):
                result['rule_cat'] = category['INACTIVE']
                result['rule_no'] = '0184'
            elif (re.search('/(?:forgery|abuse)/is', diagnosisCode)):
                result['rule_cat'] = category['INACTIVE']
                result['rule_no'] = '0196'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*restrict/is', diagnosisCode)):
                result['rule_cat'] = category['INACTIVE']
                result['rule_no'] = '0209'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*locked/is', diagnosisCode)):
                result['rule_cat'] = category['INACTIVE']
                result['rule_no'] = '0228'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user) refused/is', diagnosisCode)):
                result['rule_cat'] = category['USER_REJECT']
                result['rule_no'] = '0156'
            elif (re.search('/sender.*not/is', diagnosisCode)):
                result['rule_cat'] = category['USER_REJECT']
                result['rule_no'] = '0206'
            elif (re.search('/Message refused/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0175'
            elif (re.search('/No permit/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0190'
            elif (re.search("/domain isn't in.*allowed rcpthost/is", diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0191'
            elif (re.search('/AUTH FAILED/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0197'
            elif (re.search('/relay.*not.*(?:permit|allow)/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0201'
            elif (re.search('/not local host/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0204'
            elif (re.search('/Unauthorized relay/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0215'
            elif (re.search('/Transaction.*fail/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0221'
            elif (re.search('/Invalid data/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0223'
            elif (re.search('/Local user only/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0224'
            elif (re.search('/not.*permit.*to/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0225'
            elif (re.search('/NotAuthorized/is', diagnosisCode)):
                result['rule_cat'] = category['COMMAND_REJECT']
                result['rule_no'] = '0225'
            elif (re.search('/Content reject/is', diagnosisCode)):
                result['rule_cat'] = category['CONTENT_REJECT']
                result['rule_no'] = '0165'
            elif (re.search("/MIME\\/REJECT/is", diagnosisCode)):
                result['rule_cat'] = category['CONTENT_REJECT']
                result['rule_no'] = '0212'
            elif (re.search('/MIME error/is', diagnosisCode)):
                result['rule_cat'] = category['CONTENT_REJECT']
                result['rule_no'] = '0217'
            elif (re.search('/Mail data refused.*AISP/is', diagnosisCode)):
                result['rule_cat'] = category['CONTENT_REJECT']
                result['rule_no'] = '0218'
            elif (re.search('/Host unknown/is', diagnosisCode)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0130'
            elif (re.search('/Host not found/i', diagnosisCode)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0130'
            elif (re.search('/Domain not found/i', diagnosisCode)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0130'
            elif (re.search('/Host or domain name not found/i', diagnosisCode)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0130'
            elif (re.search('/Specified domain.*not.*allow/is', diagnosisCode)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0180'
            elif (re.search('/No route to host/is', diagnosisCode)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0188'
            elif (re.search('/unrouteable address/is', diagnosisCode)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0208'
            elif (re.search('/System.*busy/is', diagnosisCode)):
                result['rule_cat'] = category['DEFER']
                result['rule_no'] = '0112'
            elif (re.search('/Resources temporarily unavailable/is', diagnosisCode)):
                result['rule_cat'] = category['DEFER']
                result['rule_no'] = '0116'
            elif (re.search('/sender is rejected/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0101'
            elif (re.search('/Client host rejected/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0102'
            elif (re.search('/MAIL FROM(.*)mismatches client IP/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0104'
            elif (re.search('/denyip/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0144'
            elif (re.search('/client host.*blocked/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0201'
            elif (re.search('/mail.*reject/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0147'
            elif (re.search('/spam.*detect/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0162'
            elif (re.search('/reject.*spam/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0216'
            elif (re.search('/SpamTrap/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0200'
            elif (re.search('/Verify mailfrom failed/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0210'
            elif (re.search('/MAIL.*FROM.*mismatch/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0226'
            elif (re.search('/spam scale/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0211'
            elif (re.search('/junk mail/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0230'
            elif (re.search('/message filtered/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0227'
            elif (re.search('/subject.*consider.*spam/is', diagnosisCode)):
                result['rule_cat'] = category['ANTISPAM']
                result['rule_no'] = '0222'
            elif (re.search('/Temporary local problem/is', diagnosisCode)):
                result['rule_cat'] = category['INTERNAL_ERROR']
                result['rule_no'] = '0142'
            elif (re.search('/system config error/is', diagnosisCode)):
                result['rule_cat'] = category['INTERNAL_ERROR']
                result['rule_no'] = '0153'
            elif (re.search('/delivery.*suspend/is', diagnosisCode)):
                result['rule_cat'] = category['DELAYED']
                result['rule_no'] = '0213'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user)(.*)invalid/i', dsn_message)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0107'
            elif (re.search('/Deferred.*No such.*(?:file|directory)/i', dsn_message)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0141'
            elif (re.search('/mail receiving disabled/i', dsn_message)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0194'
            elif (re.search('/bad.*(?:alias|account|recipient|address|email|mailbox|user)/i', dsn_message)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '227'
            elif (re.search('/over.*quota/i', dsn_message)):
                result['rule_cat'] = category['FULL']
                result['rule_no'] = '0131'
            elif (re.search('/quota.*exceeded/i', dsn_message)):
                result['rule_cat'] = category['FULL']
                result['rule_no'] = '0150'
            elif (re.search("/exceed.*\n?.*quota/i", dsn_message)):
                result['rule_cat'] = category['FULL']
                result['rule_no'] = '0187'
            elif (re.search('/(?:alias|account|recipient|address|email|mailbox|user).*full/i', dsn_message)):
                result['rule_cat'] = category['FULL']
                result['rule_no'] = '0132'
            elif (re.search('/space.*not.*enough/i', dsn_message)):
                result['rule_cat'] = category['FULL']
                result['rule_no'] = '0219'
            elif (re.search('/Deferred.*Connection (?:refused|reset)/i', dsn_message)):
                result['rule_cat'] = category['DEFER']
                result['rule_no'] = '0115'
            elif (re.search('/Invalid host name/i', dsn_message)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0109'
            elif (re.search('/Deferred.*No route to host/i', dsn_message)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0109'
            elif (re.search('/Host unknown/i', dsn_message)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0140'
            elif (re.search('/Name server timeout/i', dsn_message)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0118'
            elif (re.search('/Deferred.*Connection.*tim(?:e|ed).*out/i', dsn_message)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0119'
            elif (re.search('/Deferred.*host name lookup failure/i', dsn_message)):
                result['rule_cat'] = category['DNS_UNKNOWN']
                result['rule_no'] = '0121'
            elif (re.search('/MX list.*point.*back/i', dsn_message)):
                result['rule_cat'] = category['DNS_LOOP']
                result['rule_no'] = '0199'
            elif (re.search('/Hop count exceeded/i', dsn_message)):
                result['rule_cat'] = category['DNS_LOOP']
                result['rule_no'] = '0199'
            elif (re.search("/I\\/O error/i", dsn_message)):
                result['rule_cat'] = category['INTERNAL_ERROR']
                result['rule_no'] = '0120'
            elif (re.search('/connection.*broken/i', dsn_message)):
                result['rule_cat'] = category['INTERNAL_ERROR']
                result['rule_no'] = '0231'
            elif (
                re.search(str("/Delivery to the following recipients failed.*\n.*\n.*" + str(result['email'])) + '/i',
                          dsn_message)):
                result['rule_cat'] = category['OTHER']
                result['rule_no'] = '0176'
            elif (re.search('/User unknown/i', dsn_message)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0193'
            elif (re.search('/Service unavailable/i', dsn_message)):
                result['rule_cat'] = category['UNKNOWN']
                result['rule_no'] = '0214'
        
        elif (action == category['DELAYED']):
            result['rule_cat'] = category['DELAYED']
            result['rule_no'] = '0110'
        elif (action == 'delivered' or action == 'relayed' or action == 'expanded'):
            pass
    if not result['bounce_type']:
        result['bounce_type'] = result['rule_cat']['bounce_type']
        result['remove'] = result['rule_cat']['permanent']
    
    return result
