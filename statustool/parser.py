import re

from statustool.calendar import CalendarEvents, Travel, Vacation
from statustool.sse_project_item import ProjectItem

__author__ = 'jshen'
__version__ = '1.0'

class RegexParser:
    def __init__(self, json_str=None):
        if json_str is not None:
            self.base_str = json_str

    def get_highlights_content(self):
        hl_list = re.findall(r"h5. Highlight(.+?)h5. /Highlight", self.base_str)
        for i in range(len(hl_list)):
            hl_list[i] = '&#8226;<span style="margin-left: 17px"></span>' + hl_list[i].replace("\\r\\n", "").replace(
                "s*", "")
        return hl_list

    def get_hotissue_content(self):
        h_list = re.findall(r"h5. Hot(.+?)h5. /Hot", self.base_str)
        for i in range(len(h_list)):
            h_list[i] = '&#8226;<span style="margin-left: 17px"></span>' + h_list[i].replace("\\r\\n", "").replace("s*",
                                                                                                                   "")
        return h_list


class JsonParser:
    def __init__(self, json, calendar_url):
        if json is not None:
            self.json = json
        self.map = {}
        ce = CalendarEvents(calendar_url=calendar_url)
        self.title, self.vacation, self.travel = ce.load_calendar()

    def generate_highlight(self):
        highlight_list = []
        issue_list = self.json['issues']
        if len(issue_list) > 0:
            for i in range(len(issue_list)):
                if issue_list[i]['fields'].get('customfield_12811') and \
                                issue_list[i]['fields']['customfield_12811'] is not None:
                    t_str = '&#8226;<span style="margin-left: 17px"></span>'
                    t_str += (issue_list[i]['fields']['customfield_12811']).replace("*", "")
                    highlight_list.append(t_str)
        return highlight_list

    def generate_hotissues(self):
        hotissue_list = []
        issue_list = self.json['issues']
        if len(issue_list) > 0:
            for i in range(len(issue_list)):
                if issue_list[i]['fields'].get('customfield_12812') and \
                                issue_list[i]['fields']['customfield_12812'] is not None:
                    tmp_arry = (issue_list[i]['fields']['customfield_12812']).split("*")
                    tmp_arry.pop(0)
                    for j in range(len(tmp_arry)):
                        tmp_arry[j] = '&#8226;<span style="margin-left: 17px"></span>' + tmp_arry[j]
                    hotissue_list.extend(tmp_arry)
        return hotissue_list

    def generate_status_detail(self, report_section_tag):
        self.map.clear()
        issue_list = self.json['issues']
        if len(issue_list) > 0:
            for i in range(len(issue_list)):
                if issue_list[i]['fields'].get('project') and issue_list[i]['fields']['project'].get('name'):
                    if not issue_list[i]['fields'].get('customfield_12120') or \
                                    issue_list[i]['fields']['customfield_12120']['value'] != report_section_tag:
                        continue
                    proj_name = issue_list[i]['fields']['project']['name']
                    if issue_list[i]['fields'].get('customfield_11102'):
                        p_item = ProjectItem(issue_list[i]['fields']['summary'], issue_list[i]['fields'].get('customfield_11102'))
                    else:
                        p_item = ProjectItem(issue_list[i]['fields']['summary'])
                    if proj_name in self.map:
                        self.map[proj_name].append(p_item)
                    else:
                        self.map.update({proj_name: [p_item]})

    def get_travel_detail(self):
        self.map.clear()

        proj_name = "TRAVEL PLANS"
        self.map.update({proj_name: []})
        for item in self.travel:
            vals = str(item).split(Travel.delimiter());
            p_item = ProjectItem(vals[0].strip(), "* " + vals[1].strip() if len(vals) > 1 else "")
            self.map[proj_name].append(p_item)

        return

    def get_vacation_detail(self):
        self.map.clear()

        proj_name = "PLANED VACATIONS"
        self.map.update({proj_name: []})
        for item in self.vacation:
            vals = str(item).split(Vacation.delimiter());
            p_item = ProjectItem(vals[0].strip(), "* " + vals[1].strip() if len(vals) > 1 else "")
            self.map[proj_name].append(p_item)
