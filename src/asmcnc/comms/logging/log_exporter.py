from datetime import datetime
import os

export_logs_folder = '/home/pi/exported_logs'


def create_log_folder():
    if not os.path.exists(export_logs_folder) or not os.path.isdir(export_logs_folder):
        os.mkdir(export_logs_folder)


def generate_logs():
    create_log_folder()

    str_current_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")

    log_name = "easycut-exported-logs-" + str_current_time + ".txt"
    full_path = export_logs_folder + '/' + log_name

    command = "journalctl > " + full_path

    os.system(command)

    return log_name


def trim_logs(log_file_path, x_lines):
    with open(log_file_path, 'w+') as untrimmed_file:
        lines = untrimmed_file.readlines()

        lines_to_remove = len(lines) - x_lines

        print('Trimming ' + str(lines_to_remove) + ' lines of ' + str(len(lines)) + ' lines')

        new_lines = lines[lines_to_remove:]

        untrimmed_file.truncate()

        untrimmed_file.writelines(new_lines)
        untrimmed_file.close()


def send_logs(log_file_path):
    pass
