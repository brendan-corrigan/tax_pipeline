import sys

from .logging import init_logging
from .pipeline import Pipeline
from .settings import Settings


def main():
    args = sys.argv[1:]
    input_path = args[0] if len(args) > 0 else "individual_tax_returns.csv"
    outdir = args[1] if len(args) > 1 else "artifacts"
    config_path = args[2] if len(args) > 2 else "configs/config.yaml"

    settings = Settings.load(config_path)
    init_logging(settings.paths.logging_config)
    pipeline = Pipeline(settings=settings)
    pipeline.run()


if __name__ == "__main__":
    main()
