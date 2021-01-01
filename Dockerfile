FROM python:2
LABEL   name="http-reflect" \
        description="What's my IP" \
        vcs-url="https://github.com/jason-matthew/http-reflect" \
        maintainer="Jon.Gates" \
        usage="curl -L reflect.example.org?host" \
        header="ZWF0IG1vcmUgY2hpY2tlbg=="

# app setup
COPY ./assets/reflect.py /app/
ENTRYPOINT [ "python", "/app/reflect.py" ]
