import os
from datetime import datetime, timedelta, timezone


class Config:
    seated = 15.00
    standing = 30.00
    up_time = 1200
    down_time = 2400


if __name__ == '__main__':
    config = Config()
    folder = r"C:\Users\vilc2301\Desktop\static"

    with open(os.path.join(folder, 'Config.txt'), 'w') as config_file:
        config_file.write(str(config.standing) + '\n')
        config_file.write(str(config.seated) + '\n')

    date = datetime(2020, 12, 5, 8, 0, 0, 0).astimezone()
    fileDay = 'Data_' + date.strftime("%Y-%m-%d") + '.dat'
    fileTimers = 'Timers_' + date.strftime("%Y-%m-%d") + '.txt'
    with open(os.path.join(folder, fileTimers), 'w') as config_file:
        config_file.write(str(config.down_time) + '\n')
        config_file.write(str(config.up_time) + '\n')

    counter = 0
    counter2 = 0
    timer = config.down_time
    height = config.seated
    expected = config.seated
    for i in range(14400):  # 4 hours of data

        # Change config (position expected)
        if counter2 == timer:
            if expected == config.seated:
                expected = config.standing
                timer = config.up_time
                counter2 = 0
            else:
                expected = config.seated
                timer = config.down_time
                counter2 = 0

        # Change position
        if counter == 1800:
            if height == config.seated:
                height = config.standing
                counter = 0
            else:
                height = config.seated
                counter = 0

        if date.hour == 9 and 30 <= date.minute <= 59:
            pass
        else:
            line = str(date.isoformat()) + "\t" + str.format("{0:.2f}\t", height) + "--" + "\t" + str.format(
                "{0:d}\t", 1) + "\t" + str.format("{0:.2f}", expected) + "\t" + str.format("{0:.2f}\t",
                                                                                           1.1) + "\t" + str.format(
                "{0:.2f}\t", 1.1) + "\t" + str.format("{0:.2f}\t", 1.1) + "\t" + str.format("{0:.2f}\t", 1.1)
            with open(os.path.join(folder, fileDay), 'a+') as file_day:
                file_day.write(line + '\n')
        date = date + timedelta(seconds=1)
        counter += 1
        counter2 += 1
