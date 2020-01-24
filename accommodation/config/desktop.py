# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "frontdesk",
			"color": "#3CB371",
			"icon": "fa fa-desktop",
			"type": "page",
			"link": "frontdesk",
			"label": _("FrontDesk"),
			"role": ('System Manager', 'Hotel Manager', 'Hotel Reservation User')
		},
		{
			"module_name": "Accommodation",
			"color": "green",
			"icon": "fa fa-home",
			"type": "module",
			"label": _("Accommodation"),
			"link": "modules/Accommodation",
			"role": ('System Manager', 'Hotel Manager', 'Hotel Reservation User')
		},
		{
			"module_name": "mahatma-search",
			"color": "#FFA07A",
			"icon": "fa fa-address-card",
			"type": "page",
			"link": "mahatma-search",
			"label": _("Mahatma Search"),
			"role": ('System Manager', 'Hotel Manager', 'Hotel Reservation User')
		},
		{
			"module_name": "room-management",
			"color": "#696969",
			"icon": "fa fa-bed",
			"type": "page",
			"link": "room-management",
			"label": _("Room Management"),
			"role": ('System Manager', 'Hotel Manager', 'Hotel Reservation User')
		},
		{
			"module_name": "Occupancy",
			"_doctype": "Accommodation Booking",
			"color": "#E59866",
			"icon": "glyphicon glyphicon-calendar",
			"type": "link",
			"link": "query-report/Occupancy",
			"role": ('System Manager', 'Hotel Manager', 'Hotel Reservation User')
		},
		{
			"module_name": "Advance Payment",
			"_doctype": "Accommodation Booking",
			"color": "green",
			"icon": "fa fa-money",
			"type": "link",
			"link": "query-report/Advance Payment",
			"role": ('System Manager', 'Hotel Manager', 'Hotel Reservation User')
		},
		{
			"module_name": "Billing",
			"_doctype": "Accommodation Booking",
			"color": "green",
			"icon": "fa fa-inr",
			"type": "link",
			"link": "query-report/Billing",
			"role": ('System Manager', 'Hotel Manager', 'Hotel Reservation User')
		},
		{
			"module_name": "Accommodation Booking",
			"_doctype": "Accommodation Booking",
			"color": "#1abc9c",
			"icon": "octicon octicon-tag",
			"type": "link",
			"link": "List/Accommodation Booking",
			"label": _("Booking"),
			"role": ('System Manager', 'Hotel Manager', 'Hotel Reservation User')
		},
		{
			"module_name": "Accommodation Guest",
			"_doctype": "Accommodation Guest",
			"color": "#8B4513",
			"icon": "fa fa-id-badge",
			"type": "link",
			"link": "List/Accommodation Guest",
			"label": _("Guest"),
			"role": ('System Manager', 'Hotel Manager', 'Hotel Reservation User')
		}
	]
