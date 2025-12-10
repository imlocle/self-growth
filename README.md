# Self Growth

An application to keep track of habits, to-dos, dailies, notes, blog, pro-con list

## Deployment

```bash
make clean && make deploy ENV=dev
```

### Deploy Lambda

```bash
# 1) Just re-zip one lambda
make zip-create-todo ENV=dev

# 2) Re-deploy with terraform
terraform -chdir=terraform apply -var="environment=dev"
```
