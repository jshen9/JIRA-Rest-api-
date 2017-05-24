
import time
import re

__author__ = 'jshen'
__version__ = '1.0'



SSE_TEMPLATE_HIGHLIGHT = '<p class="MsoListParagraph" style="text-indent: -0.25in;"><!--[if !supportLists]-->' \
                         '<span style="font-family: Symbol; color: rgb(0, 176, 80);"><span style=""> ' \
                         '<span style="font-family: &quot;Times New Roman&quot;; font-style: normal; font-variant: normal; ' \
                         'font-weight: normal; font-size: 7pt; line-height: normal; font-size-adjust: none; font-stretch: normal;">' \
                         '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></span></span><!--[endif]--><b>' \
                         '<span style="color: rgb(0, 176, 80);">%%CONTENT%%<br><o:p></o:p></span></b></p>'

SSE_TEMPLATE_HOT_ISSUE = '<p class="MsoListParagraphCxSpFirst" style="text-indent: -0.25in;"><!--[if !supportLists]-->' \
                         '<span style="font-family: Symbol; color: black;"><span style=""> ' \
                         '<span style="font-family: &quot;Times New Roman&quot;; font-style: normal; font-variant: normal; ' \
                         'font-weight: normal; font-size: 7pt; line-height: normal; font-size-adjust: none; ' \
                         'font-stretch: normal;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></span></span>' \
                         '<!--[endif]--><span style="font-weight: bold; color: red;">%%CONTENT%%</span><o:p></o:p></p>'

SSE_TEMPLATE_PROJECT_ITEM_HEADER = '<div class="WordSection1" style="margin-left: 40px; font-family: Calibri;"><p>' \
                                   '<h4 style="font-weight: 700; font-size: medium">%%CONTENT%%</h4></p>%%SUBITEM_CONTENT%%</div><br>'

SSE_TEMPLATE_PROJECT_ITEM_HEADER2 = '<div class="WordSection1" style="margin-left: 40px; font-family: Calibri;"><p>' \
                                   '<small></small></p>%%SUBITEM_CONTENT%%</div><br>'

SSE_TEMPLATE_PROJECT_ITEM_NAME = '<ul>%%NAME%%%%SUBITEM%%</ul>'

SSE_TEMPLATE_PROJECT_ITEM_SUBITEM = '%%ITEM%%%%SUBITEM%%'


class HtmlReportTemplate:
    def __init__(self, template_file):
        self.template_file = template_file
        with open(self.template_file, "r") as template_file:
            self.data = template_file.read()

        if len(self.data) > 0:
            self.init_template()

        self.highlights = []
        self.hotissues = []

    def get_template_str(self):
        return self.data

    def init_template(self):
        self.data = self.data.replace("%%TIMESTAMP%%", time.strftime("%b-%d-%Y"))

    def add_highlight(self, content):
        self.highlights.append(SSE_TEMPLATE_HIGHLIGHT.replace("%%CONTENT%%", content))

    def add_hot_issue(self, content):
        self.hotissues.append(SSE_TEMPLATE_HOT_ISSUE.replace("%%CONTENT%%", content))

    def generate_highlights(self):
        if len(self.highlights) > 0:
            highlight_str = "\n".join(self.highlights)
        else:
            highlight_str = ""
        self.data = self.data.replace("<div>%%HIGHLIGHTS%%</div>", highlight_str)

    def generate_hotissues(self):
        if len(self.hotissues) > 0:
            hotissue_str = "\n".join(self.hotissues)
        else:
            hotissue_str = ""
        self.data = self.data.replace("<div>%%HOTISSUE%%</div>", hotissue_str)

    def generate_content(self, map, tag, show_project):
        html_str = ""
        if len(map) >0:
            for key, value in map.items():
                if show_project:
                    header = SSE_TEMPLATE_PROJECT_ITEM_HEADER.replace("%%CONTENT%%", key)
                else:
                    header = SSE_TEMPLATE_PROJECT_ITEM_HEADER2
                if len(value) == 0:
                    continue
                name_section_str = ""
                for item in value:
                    item_name_section = SSE_TEMPLATE_PROJECT_ITEM_NAME.replace("%%NAME%%", "<li>" + item.get_name() + "</li>")

                    sub_html_str = ""
                    item_list = item.get_detail().split("\r\n")
                    sub_html_str = HtmlReportTemplate.format_ident_items(item_list)

                    item_detail_section = SSE_TEMPLATE_PROJECT_ITEM_SUBITEM.replace("%%ITEM%%", sub_html_str)
                    item_detail_section = item_detail_section.replace("%%SUBITEM%%", "")
                    item_name_section = item_name_section.replace("%%SUBITEM%%", item_detail_section)
                    name_section_str += item_name_section
                header = header.replace("%%SUBITEM_CONTENT%%", name_section_str)
                html_str += header

        self.data = self.data.replace(tag, html_str)
        return

    #def generate_calendar_content(self, travel, vacation):


    g_index = 0

    @staticmethod
    def format_sub_items(item_list, indent_level):
        global g_index
        if len(item_list) == 0 or g_index >= len(item_list):
            return ""

        format_str = ""
        was_indent_level = indent_level
        if g_index < len(item_list) and item_list[g_index].startswith("* "):
            if indent_level < 1:
                format_str = "<ul>"
                indent_level += 1
            format_str += "<li>" + re.sub('^\* ', '', item_list[g_index]) + "</li>"
            g_index += 1
            format_str += HtmlReportTemplate.format_sub_items(item_list, indent_level)
            if was_indent_level < 1:
                format_str += "</ul>"
        if g_index < len(item_list) and item_list[g_index].startswith("** "):
            if indent_level < 2:
                format_str = "<ul>"
                indent_level += 1
            format_str += "<li>" + re.sub('^\*\* ', '', item_list[g_index]) + "</li>"
            g_index += 1
            format_str += HtmlReportTemplate.format_sub_items(item_list, indent_level)
            if was_indent_level < 2:
                format_str += "</ul>"
        if g_index < len(item_list) and item_list[g_index].startswith("*** "):
            if indent_level < 3:
                format_str = "<ul>"
                indent_level += 1
            format_str += "<li>" + re.sub('^\*\*\* ', '', item_list[g_index]) + "</li>"
            g_index += 1
            format_str += HtmlReportTemplate.format_sub_items(item_list, indent_level)
            if was_indent_level < 3:
                format_str += "</ul>"

        return format_str

    @staticmethod
    def format_ident_items(item_list):
        global g_index
        g_index = 0
        if len(item_list) == 0:
            return ""

        format_str = ""
        while g_index < len(item_list):
            if g_index < len(item_list) and item_list[g_index].startswith("h5. "):
                format_str += re.sub('^h5\. ', '<h5>', item_list[g_index])
                format_str += "</h5>"

            if g_index < len(item_list) and item_list[g_index].startswith("*"):
                t_str = HtmlReportTemplate.format_sub_items(item_list, 0)
                format_str += t_str

            if g_index < len(item_list) and len(item_list[g_index]) == 0:
                format_str += ""

            g_index += 1
        return format_str
