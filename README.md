# LinuxForHealth EDI

![GitHub License](https://img.shields.io/github/license/linuxforhealth/edi)
![Supported Versions](https://img.shields.io/badge/python%20version-3.8%2C%203.9-blue)
<br>
![Template CI](https://github.com/linuxforhealth/edi/actions/workflows/continuous-integration.yml/badge.svg)
![Image Build](https://github.com/linuxforhealth/edi/actions/workflows/image-build.yml/badge.svg)
<br>
![GitHub Issues](https://img.shields.io/github/issues/dixonwhitmire/fastapi-template)
![GitHub Forks](https://img.shields.io/github/forks/dixonwhitmire/fastapi-template)
![GitHub Stars](https://img.shields.io/github/stars/dixonwhitmire/fastapi-template)

## Overview

LinuxForHealth EDI detects, validates, and transforms standard healthcare data formats.

### Required Software
The edi development environment requires the following:

- [git](https://git-scm.com) for project version control
- [mkcert](https://github.com/FiloSottile/mkcert) for local trusted certificates
- [Python 3.8 or higher](https://www.python.org/downloads) for runtime/coding support
- [Pipenv](https://pipenv.pypa.io) for Python dependency management  
- [Docker Compose](https://docs.docker.com/compose/install/) for a local container runtime

For Windows 10 users, we suggest using [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10)

### Set Up A Local Environment
#### Clone the project and navigate to the root directory
```shell
git clone https://github.com/linuxforhealth/edi
cd edi
```

#### Confirm that Python build tooling, pip and pipenv are installed
```shell
pip --version
pipenv --version
```

#### Install core and dev dependencies
```shell
pip install --upgrade pip
pipenv sync --dev
```

#### Run tests
```shell
pipenv run pytest
```

#### Black code formatting integration

edi utilizes the [black library](https://black.readthedocs.io/en/stable/index.html) to provide standard code formatting. Code formatting and style are validated as part of the [continuous integration process](./.github/workflows/continuous-integration.yml). edi provides developers with an option of formatting using pipenv scripts, or a git pre-commit hook.

#### Pipenv Scripts

##### Check for formatting errors
```shell
pipenv run check-format
```

##### Format code
```shell
pipenv run format
```

#### Git pre-commit hook integration

##### Install git pre-commit hooks (initial setup)
```shell
pipenv run pre-commit install
```

##### Commit Output - No Python Source Committed
```shell
black................................................(no files to check)Skipped
[black-formatter 95bb1c6] settings black version to latest release
 1 file changed, 1 insertion(+), 1 deletion(-)
```

##### Commit Output - Python Source is Correctly Formatted
```shell
black....................................................................Passed
[format-test c3e1b4a] test commit
 1 file changed, 1 insertion(+)
```

##### Commit Output - Black Updates Python Source
```shell
black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted edi/routes/api.py
All done! ✨ 🍰 ✨
1 file reformatted.
```

#### Generate trusted local certs for edi and its supporting services
```shell
./local-config/install-certificates.sh
```
For more information on edi and HTTPS/TLS support, please refer to [the local cert readme](local-config/README.md).


#### Start app and supporting services
```shell
docker-compose up -d
docker-compose ps
pipenv run edi
```

Browse to `https://localhost:5000/docs` to view the Open API documentation

### Docker Image
The edi docker image is an "incubating" feature and is subject to change. The image is associated with the "deployment" profile to provide separation from core services.

#### Build the image
The edi image build integrates the application's x509 certificate (PEM encoded) into the image.

The `APP_CERT_PATH_BUILD_ARG` build argument is used to specify the location of the certificate on the host machine.
If the `APP_CERT_PATH_BUILD_ARG` build argument is not provided, a default value of ./local-config/app is used.

#### Build the image with Docker CLI
```shell
docker build \
       --build-arg APP_CERT_PATH_BUILD_ARG=./local-config/ \ 
       --build-arg APP_CONFIG_PATH_BUILD_ARG=./local-config/ \
       -t edi:0.42.0 .
```

#### Build the image with Docker-Compose
The docker-compose command below parses the build context, arguments, and image tag from the docker-compose.yaml file.
```shell
docker-compose build edi
```

#### Run edi and Supporting Services
```shell
docker-compose up -d
```
