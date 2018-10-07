import configuration
import data
import display
import events


if __name__ == '__main__':
    configuration.setup_logging()
    configuration.setup_config()

    data = data.Data()
    data.schedule_data_download()

    display = display.Display(data, events.change_mode)
    display.start()
