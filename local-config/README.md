# Local Configuration

This project directory contains configuration tooling to support running edi, and it's dependent services locally for development use. Contents include:

* install-certificates.sh - a shell script used to generate a locally trusted Root CA and self-signed certificates.
* uninstall-certificates.sh - a shell script used to remove generated certificates.
* app - contains application configuration files and certificates

## Local Trusted Certificates

App is configured to support secure transmissions (HTTPS/SSL/TLS) for core and external services.
[mkcert](https://github.com/FiloSottile/mkcert) is used to implement secure processing for local/development deployments. Please note that mkcert is not recommended for production use.
External/deployed environments are expected to utilize valid non-self signed certificates.

App uses base-64 encoded "PEM" formatted keys and certificates.


### mkcert certificate support

#### Create certificates
```shell
./local-config/install-certificates.sh
```

#### Remove certificates
```shell
./local-config/uninstall-certificates.sh
```
