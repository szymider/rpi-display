import argparse
import logging
import sys

from jsonschema import ValidationError

from rpidisplay import configuration
from rpidisplay import data
from rpidisplay import display

log = logging.getLogger('main')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', type=str, help='Config location path', default='./config')
    ap.add_argument('-f', type=str, help='Config file name (without .yml extension)', default='config')
    args = ap.parse_args()

    configuration.setup_logging()
    configuration.setup_config(args.p, args.f)

    try:
        configuration.validate_config()
    except ValidationError as e:
        log.error(".".join(x for x in e.path if isinstance(x, str)) + ": " + e.message)
        sys.exit(1)

    d = data.Data()
    d.schedule_data_download()

    dp = display.Display(d)
    dp.start()


if __name__ == '__main__':
    main()
