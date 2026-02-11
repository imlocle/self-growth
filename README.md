# Self Growth

An application to keep track of habits, to-dos, dailies, notes, blog, pro-con list

- Python 3.13
- Terraform

## Set Up

### Python Environment & Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
```

## Deployment

Usage:

```bash
make deploy ENV=dev
```

Force Rebuild Layer:

```bash
make rebuild-layer ENV=dev
```

Full Reset:

```bash
make nuke && make deploy ENV=dev
```

## Update Lambda

Build only one Lambda zip:

```bash
make zip-create-todo ENV=dev
```

Deploy only one Lambda (build its zip, then terraform apply):

```bash
make deploy-create-todo ENV=dev
```
