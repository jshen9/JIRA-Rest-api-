

import datetime
from restful_lib import Connection
from icalendar import Calendar

class EventEntry(object):
    def __init__(self, summary, organizer, attendee, start, stop):
        self.summary = summary
        self.organizer = organizer
        self.attendee = attendee
        self.start = start
        self.stop = stop

    def __str__(self):
        return "{summary} @ {start} - {end}".format(summary=self.summary, start=self.start, end=self.stop)


class Vacation(EventEntry):
    def __str__(self):
        template = "{who} @ {start} - {end}"
        if self.start == self.stop:
            template = "{who} @ {start}"
        return template.format(who=self.attendee, start=self.start, end=self.stop)


    @staticmethod
    def delimiter():
        return "@"


class Travel(EventEntry):
    def __str__(self):

        why = self.summary
        if self.attendee in self.summary:
            start_summary = self.summary.find(": ")
            if start_summary != -1:
                why = self.summary[start_summary + 2:]

        template = "{who} + {why} @ {start} - {end}"
        if self.start == self.stop:
             template = "{who} + {why} @ {start}"
        return template.format(who=self.attendee, start=self.start, end=self.stop, why=why)

    @staticmethod
    def delimiter():
        return "+"

class EasyCal(object):
    """provides simple access to leave and travel events"""

    def __init__(self, calendar, skip_old_events=True):
        self.skip_old_events = skip_old_events
        self.calendar = calendar

        self.name = self.calendar.get("X-WR-CALNAME")
        self.description = self.calendar.get("X-WR-CALDESC")

    def _events_by_type(self, subcalendar_type, cutoff_date=None):
        cutoff_date = datetime.datetime.combine(cutoff_date, datetime.time(0, 0))
        for event in self.calendar.walk("vevent"):
            today = datetime.datetime.today()
            today = datetime.datetime.combine(today, datetime.time(0, 0))
            start = event.get("dtstart").dt
            start = datetime.datetime.combine(start, datetime.time(0, 0))
            end = event.get("dtend").dt
            end = datetime.datetime.combine(end, datetime.time(0, 0)) - datetime.timedelta(minutes=1)
            if self.skip_old_events and (start < today or end < today):
                continue
            if cutoff_date:
                if start > cutoff_date:
                    continue

            if subcalendar_type.lower() == event.get("X-CONFLUENCE-SUBCALENDAR-TYPE").lower():
                yield event

    def _entries_per_event(self, event, entry_class=EventEntry):
        tmp_attendees = event.get("attendee")
        if isinstance(tmp_attendees, list):
            attendees = [user.params["CN"] for user in tmp_attendees]
        else:
            attendees = [tmp_attendees.params["CN"], ]

        for attendee in attendees:

            end = event.get("dtend").dt
            if isinstance(end,datetime.date):
                end_dt = (datetime.datetime.combine(end, datetime.time(0,0)) - datetime.timedelta(minutes=1))
                end = end_dt.date()


            yield entry_class(
                summary=event.get("summary"),
                organizer=event.get("organizer").params["CN"],
                attendee=attendee,
                start=event.get("dtstart").dt,
                stop=end
            )

    def _entries_per_type(self, subcalendar_type, entry_class=EventEntry, cutoff_date=None):
        result = list()
        for event in self._events_by_type(subcalendar_type, cutoff_date):
            for entry in self._entries_per_event(event, entry_class):
                result.append(entry)
        return result

    def get_vacation_events(self, cutoff_date=None):
        return self._entries_per_type("leaves", Vacation, cutoff_date)

    def get_travel_events(self, cutoff_date=None):
        return self._entries_per_type("travel", Travel, cutoff_date)

    @classmethod
    def from_url(cls, calendar_url, verify_ssl=False, skip_old_events=True):
        conn = Connection(calendar_url)
        resp, request_data = conn.simple_request(calendar_url)

        if resp.status != 200 and resp.status != 304:
            msg = 'Error status code: %s - reason: %s' % (resp.status, resp.reason)
            raise Exception(msg)

        return cls(Calendar.from_ical(request_data), skip_old_events=skip_old_events)

class CalendarEvents:

    def __init__(self, calendar_url):
        self.calendar_url = calendar_url

    def load_calendar(self):
        print "Loading calendar....",
        try:

            cal = EasyCal.from_url(self.calendar_url)
            cutof_date = datetime.date.today() + datetime.timedelta(weeks=6)

            dateformat = "{today} and {cutoff}\n".format(today=datetime.date.today(), cutoff=cutof_date)
            title = "%s - %s" % (cal.name, dateformat)

            vacation = []
            for v in sorted(cal.get_vacation_events(cutof_date), key=lambda x: x.start):
                vacation.append(v)

            travel = []
            for v in sorted(cal.get_travel_events(cutof_date), key=lambda x: x.start):
                travel.append(v)

            return title, vacation, travel
        except Exception as exp:
            print "could not get calendar - %s" % exp
