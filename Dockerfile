FROM python:3.9.4-alpine3.13

ARG EDI_CERT_PATH_BUILD_ARG="./local-config/edi"
ARG EDI_CONFIG_PATH_BUILD_ARG="./local-config/edi"

# include build toolchain for linked c libraries
RUN apk update && \
    apk add ca-certificates && \
    apk add --no-cache --virtual .dev-packages bash \
        build-base \
        curl \
        openssl

# install certificates
# copy certificates and keys
WORKDIR /usr/local/share/ca-certificates/
COPY $EDI_CERT_PATH_BUILD_ARG/*.pem ./
COPY $EDI_CERT_PATH_BUILD_ARG/*.key ./
RUN chmod 644 *.pem *.key
RUN update-ca-certificates

# configure the app
RUN addgroup -S lfh && adduser -S lfh -G lfh -h /home/lfh

USER  lfh

WORKDIR /home/lfh/edi
# copy config files
RUN mkdir config
COPY --chown=lfh:lfh Pipfile.lock logging.yaml ./

# configure application
COPY --chown=lfh:lfh ./edi ./edi
RUN python -m pip install --user --upgrade pip pipenv
RUN /home/lfh/.local/bin/pipenv sync

# hang onto dev packages until python libs are installed. Required for native dependencies.
USER root
RUN apk del .dev-packages

USER lfh
EXPOSE 5000
WORKDIR /home/lfh/edi
ENV PYTHONPATH="."
CMD ["/home/lfh/.local/bin/pipenv", "run", "python", "edi/main.py"]
