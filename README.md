# MPESA-BTOBET-CLIENT

A simple wrapper (API) that sits between [MPESA](https://www.safaricom.co.ke/personal/m-pesa) and [BtoBet](https://www.btobet.com/), allowing 3rd party clients to seamlessly process payments (B2B, B2C and C2B).


TODO:

- [ ] B2B flow
- [ ] B2C flow
- [ ] C2B (partially, the **Broker** has been implemented)
- [ ] Unit Tests
- [ ] CI/CD (Github Actions or/and GitLab CI)

## Usage

Prerequisite:

- [git](https://git-scm.com/)
- [Python 3.12](https://www.python.org/downloads/release/python-3120/) or later.
- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/)

### Development

Without [Docker](https://www.docker.com/):

```bash
git clone git@github.com:clovisphere/mpesa-btobet-client.git
cd mpesa-btobet-client
poetry install
export PYTHONDONTWRITEBYTECODE=1  # you don't have to do this:-)
export DATABASE_URL=sqlite:///./demo.db
```

If you are using the [zed](https://zed.dev/) code editor, please add the below to [./pyproject.toml](pyproject.toml):

```toml
[tool.pyright]
venvPath = ""  # absolute path to your `virtualenvs` folder
venv = ""      # venv name
```

Setup the database (fresh start, with no revision):

```bash
alembic current                            # check db state
alembic revision --autogenerate -m "init"  # initialize database
alembic upgrade head                       # apply migration(s)
```

Use the below if revision(s) exist in [versions](./alembic/versions):

```bash
alembic current                  # check db state
alembic upgrade head             # apply migration(s)
```

To learn more about alembic [here](https://alembic.sqlalchemy.org/en/latest/).

#### SQLite3 (for dummies 😂)

```console
$ sqlite3 demo.db                   # access sqlite console from your terminal

sqlite> .headers ON
sqlite> .mode columns
sqlite> .tables                     # show all tables
sqlite> .schema deposit             # equivalent to MySQL's `DESC deposit;`
sqlite> pragma table_info(deposit); # same as ☝🏽
sqlite> select * from deposit;      # view (all) table data
sqlite> .exit                       # exit the sqlite3 console
```

We will use a [Makefile](./Makefile) to start the app 🤗

```bash
make local-dev
```

With [Docker](https://www.docker.com/):


```bash
make build-start-container-dev
```

Test it out:

1. [/health](http://localhost:8088/health)
2. [swagger ui](http://localhost:8088/docs)

with [httpie](https://httpie.io/):

```http :8088/health```

you'd get:

```json
{
    "status": "healthy 😊"
}
```

To bring down the containers and volumes down once done:

```bash
make stop-container
```

You can read and learn about Makefiles [here](https://opensource.com/article/18/8/what-how-makefile).

### Production

```bash
make build-start-container-prod DATABASE_URL=url_to_your_prod_db
```

## Author

Clovis Mugaruka

- [github.com/clovisphere](https://github.com/clovisphere)
- [twitter/clovisphere](https://twitter.com/clovisphere)

### License

Copyright ©️ 2023, [Clovis Mugaruka](https://clovisphere.com).\
Released under the [MIT License](./LICENSE).
