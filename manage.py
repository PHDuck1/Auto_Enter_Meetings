from calendar_api import CalendarProcessor
import webbrowser


def main():
    calendar = CalendarProcessor()
    next = calendar.get_next_meetings()
    print(*next, sep='\n')

if __name__ == '__main__':
    main()