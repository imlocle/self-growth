An API application to keep track of habits, to-dos, dailies, notes, blog post, pro-con list.

# Technology

- Python: v3.12.0
- pyenv
- [Flask](https://flask.palletsprojects.com/en/3.0.x/)

## Environment

Create a virtual environment.

```bash
python -m venv .venv
```

Activate virtual environment.

```bash
source .venv/bin/activate
```

## Install Dependencies

Go to `api` directory then input:

```bash
pip install -r requirements.txt
```

## Run

```bash
flask run
```

### Create database migration

  ```bash
  alembic revision --autogenerate -m "Description here"
  ```

### Run database migrations

  ```bash
  alembic upgrade head
  ```
