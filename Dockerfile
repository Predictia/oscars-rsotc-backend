FROM ghcr.io/prefix-dev/pixi:latest

# Set working directory
WORKDIR /code

# Copy configuration files
COPY pyproject.toml /code/pyproject.toml
COPY pixi.toml /code/pixi.toml
COPY README.md /code/README.md
COPY LICENSE /code/LICENSE

# Copy source code and docs
COPY ./app /code/app
COPY ./main.py /code/main.py
COPY ./docs /code/docs

# Install dependencies
RUN pixi install && pixi clean

# Build Sphinx HTML
RUN pixi run docs-build

# Expose FastAPI port
EXPOSE 8000

# Start the FastAPI app using pixi run
CMD ["pixi", "run", "dev"]
