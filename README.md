# MPESA-BTOBET-CLIENT

A simple wrapper (API) that sits between [MPESA](https://www.safaricom.co.ke/personal/m-pesa) and [BtoBet](https://www.btobet.com/), allowing 3rd party clients to seamlessly process payments (B2B, B2C and C2B).


TODO:

- [ ] B2B
- [ ] B2C
- [x] C2B (partially, the broker has been implemented)

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

1. [http:localhost:8088/docs](http:localhost:8088/docs)

To bring down the containers and volumes down once done:

```bash
make stop-container
```

You can read and learn about Makefiles [here](https://opensource.com/article/18/8/what-how-makefile).

### Production

- [ ] docker-compose.prod.yml


## Author

Clovis Mugaruka

- [github.com/clovisphere](https://github.com/clovisphere)
- [twitter/clovisphere](https://twitter.com/clovisphere)

### License

Copyright ©️ 2023, [Clovis Mugaruka](https://clovisphere.com).\
Released under the [MIT License](./LICENSE).
