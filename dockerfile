FROM python:3.11-bookworm

RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
ENV XMLTV_URL=
ENV TZ=

WORKDIR /epghub

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --no-dev --no-root && rm -rf $POETRY_CACHE_DIR

COPY xmltv.dtd ./xmltv.dtd
COPY epg ./epg
COPY main.py ./main.py
COPY scheduler.py ./scheduler.py
COPY templates ./templates
COPY config ./_config

CMD if [ ! -f /epghub/config/channels.yaml ]; then cp /epghub/_config/channels.yaml /epghub/config/channels.yaml; fi \
    && poetry run python main.py \
    && poetry run python scheduler.py
