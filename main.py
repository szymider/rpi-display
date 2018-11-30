import argparse

from rpidisplay import configuration
from rpidisplay import data
from rpidisplay import display


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', type=str, help='Config location path', default='./config')
    ap.add_argument('-f', type=str, help='Config file name (without .yml extension)', default='config')
    args = ap.parse_args()

    configuration.setup_logging()
    configuration.setup_config(args.p, args.f)
    configuration.validate_config()

    d = data.Data()
    d.schedule_data_download()

    dp = display.Display(d)
    dp.start()


if __name__ == '__main__':
    main()
