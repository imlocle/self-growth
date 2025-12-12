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

```bash
make clean && make deploy ENV=dev
```

### Update Lambda

```bash
# 1) Just re-zip one lambda
make zip-create-todo ENV=dev

# 2) Re-deploy with terraform
terraform -chdir=terraform apply -var="environment=dev" -auto-approve
```
