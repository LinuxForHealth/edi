FROM python:3.9.4-alpine3.13

ARG APP_CERT_PATH_BUILD_ARG="./local-config/app"
ARG APP_CONFIG_PATH_BUILD_ARG="./local-config/app"

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
COPY $APP_CERT_PATH_BUILD_ARG/*.pem ./
COPY $APP_CERT_PATH_BUILD_ARG/*.key ./
RUN chmod 644 *.pem *.key
RUN update-ca-certificates

# configure the app
RUN addgroup -S appgroup && adduser -S appuser -G appgroup -h /home/appuser

USER  appuser

WORKDIR /home/appuser/app
# copy config files
RUN mkdir config
COPY --chown=appuser:appuser Pipfile.lock logging.yaml ./

# configure application
COPY --chown=appuser:appuser ./app ./app
RUN python -m pip install --user --upgrade pip pipenv
RUN /home/appuser/.local/bin/pipenv sync

# hang onto dev packages until python libs are installed. Required for native dependencies.
USER root
RUN apk del .dev-packages

USER appuser
EXPOSE 5000
WORKDIR /home/appuser/app
ENV PYTHONPATH="."
CMD ["/home/appuser/.local/bin/pipenv", "run", "python", "app/main.py"]
