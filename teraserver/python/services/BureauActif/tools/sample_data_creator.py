from datetime import datetime, timedelta, timezone

if __name__ == '__main__':
    date = datetime(2020, 3, 4, 8, 0, 0, 0).astimezone()
    f = open(r"C:\Users\tubbs\Desktop\New\Data_2020-12-04.dat", "a")

    counter = 0
    counter2 = 0
    standing = False
    height = 15.00
    expected = 15.00
    for i in range(14400):

        if counter2 == 5400:
            if expected == 15.00:
                expected = 30.00
                counter2 = 0
            else:
                expected = 15.00
                counter2 = 0

        if counter == 1800:
            if height == 15.00:
                height = 30.00
                counter = 0
            else:
                height = 15.00
                counter = 0
            standing = not standing

        if date.hour == 9 and 30 <= date.minute <= 59:
            pass
        else:
            f.write(str(date.isoformat()) +
                    "\t" + str.format("{0:.2f}\t", height) + "--" + "\t" +
                    str.format("{0:d}\t", 1) +
                    "\t" + str.format("{0:.2f}", expected) +
                    "\t" + str.format("{0:.2f}\t", 1.1) +
                    "\t" + str.format("{0:.2f}\t", 1.1) +
                    "\t" + str.format("{0:.2f}\t", 1.1) +
                    "\t" + str.format("{0:.2f}\t", 1.1) + "\n")
        date = date + timedelta(seconds=1)
        counter += 1
        counter2 += 1

    f.close()
