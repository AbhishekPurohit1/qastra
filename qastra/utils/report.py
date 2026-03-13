import time


def log_result(test_name, status):

    with open("report.txt", "a", encoding="utf-8") as f:

        f.write(
            f"{time.ctime()} | {test_name} | {status}\n"
        )

