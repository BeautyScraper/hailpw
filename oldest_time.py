from datetime import datetime
import os

if os.path.exists("oldest_datetime.txt"):
    os.remove("oldest_datetime.txt")

def update_oldest_datetime(dates, filename="oldest_datetime.txt"):
    """
    Finds the oldest datetime from the given list and updates the file
    only if it's older than the currently stored datetime.
    
    :param dates: List of datetime strings in format "DD Mon YYYY HH:MM:SS"
    :param filename: File to store the oldest datetime
    """
    
    fmt = "%d %b %Y %H:%M:%S"  # datetime format
    parsed_dates = [datetime.strptime(d, fmt) for d in dates]
    oldest_in_list = min(parsed_dates)

    # Read current oldest from file (if exists)
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read().strip()
            if content:
                try:
                    current_oldest = datetime.strptime(content, fmt)
                except ValueError:
                    current_oldest = None
            else:
                current_oldest = None
    else:
        current_oldest = None

    # Compare and update if needed
    if current_oldest is None or oldest_in_list < current_oldest:
        with open(filename, "w") as f:
            f.write(oldest_in_list.strftime(fmt))
        print(f"✅ Updated file with: {oldest_in_list.strftime(fmt)}")
    else:
        print(f"ℹ️ No update needed. Oldest in file: {current_oldest.strftime(fmt)}")


def main():
    # Example usage
    dates = [
        '27 Sep 2025 10:50:46',
        '27 Sep 2025 10:39:53',
        '27 Sep 2025 10:38:58',
        '27 Sep 2025 10:37:42'
    ]
    update_oldest_datetime(dates, "oldest_datetime.txt")


if __name__ == "__main__":
    main()
