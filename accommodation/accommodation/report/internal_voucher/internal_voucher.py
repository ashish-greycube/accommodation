# Copyright (c) 2013, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _, scrub
from frappe.utils import getdate, nowdate, flt, cint, cstr


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    """return columns"""
    columns = [
        _("Email") + ":Data:90",
        _("Approve") + ":Data:90",
        _("Reject") + ":Data:90",
        _("Invoice") + ":Link/Sales Invoice:100",
        _("Sale Date") + ":Date:90",
        _("Department") + ":Data:160",
        _("Instructed By") + ":Data:160",
        _("Amount") + ":Currency:100",
        _("Status") + ":Data:100",
    ]
    return columns


def get_data(filters):
    data = frappe.db.sql(
        """
select
    '<a href="#" onclick="return false;">Email</a>',
    '<a href="#" onclick="return false;">Approve</a>',
    '<a href="#" onclick="return false;">Reject</a>',
    name,
    posting_date,
    customer,
    customer_name,
    rounded_total,
    status
from
    `tabSales Invoice`
        {conditions}
        order by customer, posting_date
    """.format(conditions=get_conditions(filters)), filters)
    return data
    # return [ (action_buttons+d) for d in data]


action_buttons = (
    ('<button class="btn">Email</button>'),
    ('<button class="btn">Approve</button>'),
    ('<button class="btn btn-danger">Reject</button>'),
)


def get_conditions(filters):
    conditions = ["customer_group = 'Internal'"]
    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
    if filters.get("customer"):
        conditions.append("customer = %(customer)s")
    if filters.get("month"):
        conditions.append("left(MONTHNAME(posting_date),3) = %(month)s")

    return "where {}".format(" and ".join(conditions)) if conditions else ""