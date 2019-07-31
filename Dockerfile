FROM python:3.7-slim-buster

# Upgrade pip and other base packages (usually not needed)
RUN pip install --no-cache-dir -U pip setuptools wheel

# Install required apt packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # Required for pretix "rebuild" command
        gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install base requirements such as pretix site, gunicorn, etc.
COPY docker_files/requirements.txt /code/docker_files/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && pip install --no-cache-dir -r /code/docker_files/requirements.txt \
    && apt-get purge --auto-remove -y \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pretix payment plugin
COPY . /code/
WORKDIR /code
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && pip install --no-cache-dir -e . \
    && apt-get purge --auto-remove -y \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Make necessary dirs/files
RUN mkdir -p \
        /data \
        /pretix/src \
    && touch /pretix/src/pretix.cfg

# Ensure site user has adequate permissions
RUN chmod -R g+rw,o+rw \
        /data \
        /pretix/src/pretix.cfg \
        /usr/local/lib/python3.7/site-packages/pretix

COPY docker_files/pretix.bash /usr/local/bin/pretix
COPY docker_files/pretix.cfg /etc/pretix/pretix.cfg
COPY docker_files/update_cfg_from_env.py /pretix/src/update_cfg_from_env.py
COPY docker_files/pretix_cfg_env_whitelist.txt /pretix/src/pretix_cfg_env_whitelist.txt
COPY docker_files/docker_settings.py /pretix/src/docker_settings.py

RUN useradd -ms /bin/bash pretixuser
USER pretixuser

RUN /usr/local/bin/pretix rebuild

CMD ["/usr/local/bin/pretix"]
