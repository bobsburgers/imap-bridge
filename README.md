Run bash ./build.sh to build docker image

Run 

```j
docker run -e EVENT_TRANSPORT=track \
-e TRACARDI_API_HOST="http://192.168.1.103:8686" \
-e TRACARDI_SOURCE_ID="55242117-9a0e-4d61-adf6-d60c2322ad45" \
-e TRACARDI_EVENT_TYPE="imap-mail" \
-e TRACARDI_USERNAME="<e-mail>" \
-e TRACARDI_PASSWORD="<password>" \
-e IMAP_HOST="<imap-server>" \
-e IMAP_PORT=993 \
-e IMAP_USERNAME="<email>" \
-e IMAP_PASSWORD="<pass>" \
-e IMAP_MAILBOX="inbox" \
-e ELASTIC_HOST="192.168.1.103" \
-e ELASTIC_VERIFY_CERTS="no" \
-e REDIS_HOST="redis://192.168.1.103:6379" \
tracardi/bridge-imap:0.7.3-dev
```
