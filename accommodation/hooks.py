# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "accommodation"
app_title = "Accommodation"
app_publisher = "DBF"
app_description = "Hotels"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@amba-tech.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
    "/assets/accommodation/css/accommodation.css",
    "/assets/accommodation/css/jquery.jexcel.css"
]
app_include_js = [
    "/assets/accommodation/js/accommodation.js",
    "/assets/accommodation/js/report_base.js",
    "/assets/accommodation/js/lib/jquery.jexcel.js",
]

# include js, css files in header of web template
# web_include_css = "/assets/accommodation/css/accommodation.css"
# web_include_js = "/assets/accommodation/js/accommodation.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "accommodation.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "accommodation.install.before_install"
# after_install = "accommodation.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "accommodation.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
    "Employee": {
        "validate": "accommodation.accommodation.controller.validate_employee"
    },
    "Sales Invoice": {
        "autoname":
        "accommodation.accommodation.controller.autoname_sales_invoice",
        "on_update":
        "accommodation.accommodation.controller.on_update_sales_invoice",
        "on_trash":
        "accommodation.accommodation.controller.on_trash_sales_invoice",
    },
    "Journal Entry": {
        "autoname":
        "accommodation.accommodation.controller.autoname_journal_entry"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"accommodation.tasks.all"
# 	],
# 	"daily": [
# 		"accommodation.tasks.daily"
# 	],
# 	"hourly": [
# 		"accommodation.tasks.hourly"
# 	],
# 	"weekly": [
# 		"accommodation.tasks.weekly"
# 	]
# 	"monthly": [
# 		"accommodation.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "accommodation.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "accommodation.event.get_events"
# }
