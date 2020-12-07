import os
from datetime import datetime, timedelta, timezone

if __name__ == '__main__':
    date = datetime(2020, 12, 6, 8, 0, 0, 0).astimezone()
    folder = r"C:\Users\vilc2301\Desktop\static"
    fileDay = 'Data_' + date.strftime("%Y-%m-%d") + '.dat'

    counter = 0
    counter2 = 0
    height = 15.00
    expected = 15.00
    for i in range(14400):  # 4 hours of data

        # Change config (position expected)
        if counter2 == 5400:
            if expected == 15.00:
                expected = 30.00
                counter2 = 0
            else:
                expected = 15.00
                counter2 = 0

        # Change position
        if counter == 1800:
            if height == 15.00:
                height = 30.00
                counter = 0
            else:
                height = 15.00
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
