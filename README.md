# Twinbase SSI API

[Twinbase API](https://github.com/juusoautiosalo/twinbase-api) is server software that provides an HTTP API to a selected GitHub-hosted Twinbase instance.

This repository combines the Twinbase API with
an [SSI component](https://gitlab.com/JuusoAut/privacy-preserving-self-sovereign-identities) 
to provide authentication with [SSI (Self-Sovereign Identity)](https://en.wikipedia.org/wiki/Self-sovereign_identity) technologies:
- DID (Decentralized Identifier) [W3C Recommendation](https://www.w3.org/TR/did-core/)
- VC (Verifiable Credential) [W3C Recommendation](https://www.w3.org/TR/vc-data-model/)

# Setup

## Clone and move to repository
```sh
git clone https://gitlab.com/JuusoAut/privacy-preserving-self-sovereign-identities.git

git clone https://github.com/juusoautiosalo/twinbase-api.git

git clone https://github.com/IoT-NGIN/twinbase-ssi-api.git

cd twinbase-ssi-api
```

## Deployment

Prerequisites
- Docker and Docker compose

### Set environment variables
Configure environment variables or `.env` file to match environment variables used in [`docker-compose.yml`](docker-compose.yml) (`${}`).
```
nano .env
```
Example contents:
```
TWINBASE_API_TWINBASE_REPO_URL="https://github.com/juusoautiosalo/twinbase-smart-city"
TWINBASE_API_GITHUB_TOKEN=github_pat_1234567890qwerty
TWINBASE_API_GITHUB_USERNAME=juusoautiosalo
IAA_OWNER_DID=did:key:z6Mkk4YdpLxAxWkDULdBVifCjVDPh3WvhbkDL1W4miwoHEQb
```
Explanations:
- `TWINBASE_API_TWINBASE_REPO_URL`: The url of the repository you want to host the SSI API for
- `TWINBASE_API_GITHUB_TOKEN`: Create a fine-grained access token at https://github.com/settings/personal-access-tokens/new
  - Repository access => Only select repsitories => [Your Twinbase instance repository]
  - Permissions => Repository permissions => Contents => Access: Read and write
  - Press "Generate token" and copy the token to the variable
- `TWINBASE_API_GITHUB_USERNAME`: The username associated with `TWINBASE_API_GITHUB_TOKEN`
- `IAA_OWNER_DID`: Create an owner DID according to instructions at https://gitlab.com/JuusoAut/privacy-preserving-self-sovereign-identities

### Start services
```
docker compose up --build --detach
```
See Swagger documentation at http://localhost:9000/docs
- Requests via the Swagger interface don't work because Swagger doesn't support SSI authentication.
- To send requests to the SSI API, set up DIDs, credentials, tokens, and headers according to these instructions:
  https://gitlab.com/JuusoAut/privacy-preserving-self-sovereign-identities


### Stop services
```
docker compose down
```

### Remove all unused docker images
```
docker image prune --all
```

## Development

Prerequisites
- Python 3.7 or above
- `make`
  - If make is not available you may check [Makefile](Makefile) for the commands

### Create virtual environment and install requirements

```sh
# Create and activate virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install pip-tools to manage requirements
make pip-tools

# Install requirements to virtual enviroment with pip-tools
make sync
```

### Build and run Twinbase API with docker
```
docker compose build iaa-configurator && docker compose run --rm iaa-configurator
```
(CTRL+C to quit)

Remove unused images
```
docker image prune --all
```

### Edit python requirements
1. Edit the requirements in [pyproject.toml](pyproject.toml)
2. Then run:
```sh
make update-dependencies
```
