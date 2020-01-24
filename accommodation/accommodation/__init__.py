# -*- coding: utf-8 -*-
# Copyright (c) 2019, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe.utils import date_diff, now_datetime, getdate, cint, flt, fmt_money
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import get_account_currency
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry, get_company_defaults
from erpnext.accounts.doctype.journal_entry.journal_entry import get_payment_entry_against_invoice

from frappe.utils import random_string


def test_invoice():
    doc = frappe.get_doc("Accommodation Booking", "BKG-2")
    doc.make_sales_invoice()


def clear_and_book():
    clear_alll()
    make_booking()


def test_payment():
    import random
    make_payment("BKG-5", random.randint(55, 99), "Cash", 0, False)


def make_booking():
    doc = frappe.get_doc({
        "doctype": "Accommodation Booking",
        "guest": "GUE-2",
        "package": "Mahatma",
        "status": "Booked",
    })
    line = doc.append("items")
    line.update({
        "check_in": '2019-01-26',
        "check_out": '2019-01-27',
        'item_status': 'Checked In',
        'room_type': 'Suite',
        'room': '114',
        'extra_bed_count': 2,
        'total_extra_bed_count': 2,
        'room_count': 1,
        'room_rate': 450.0,
        'bed_rate': 100.0,
        'amount': 650.0
    })
    doc.insert()
    frappe.db.commit()


def clean_transactions():
    '''Cleans Booking, Sales Invoice, Journal Entries'''

    for d in frappe.get_list("Accommodation Booking"):
        print(d)
        frappe.delete_doc("Accommodation Booking", d.name)

    for d in frappe.get_list("Sales Invoice", {"docstatus": 1}):
        frappe.get_doc("Sales Invoice", d.name).cancel()
    for d in frappe.get_list("Sales Invoice"):
        print(d)
        frappe.delete_doc("Sales Invoice", d.name)

    for d in frappe.db.get_list("Journal Entry", {"docstatus": 1}):
        frappe.get_doc("Journal Entry", d.name).cancel()
    for d in frappe.db.get_list("Journal Entry"):
        print(d)
        frappe.delete_doc("Journal Entry", d.name)
    frappe.db.commit()


def clear_all():

    # Sales Invoice
    for d in frappe.db.get_list("Accommodation Booking"):
        frappe.db.set_value("Accommodation Booking", d.name, "invoice", None)
    for d in frappe.db.get_list("Sales Invoice", filters={"docstatus": 1}):
        frappe.get_doc("Sales Invoice", d["name"]).cancel()
    frappe.db.commit()

    for d in frappe.db.get_list("Sales Invoice"):
        doc = frappe.get_doc("Sales Invoice", d.name).delete()
    frappe.db.commit()

    # Journal Entry
    for d in frappe.db.get_list("Journal Entry", filters={"docstatus": 1}):
        doc = frappe.get_doc("Journal Entry", d["name"])
        for i in doc.accounts:
            frappe.db.set_value("Journal Entry Account", i.name,
                                "reference_name", None)
            frappe.db.set_value("Journal Entry Account", i.name,
                                "reference_type", None)
        frappe.db.commit()
        doc.cancel()
    frappe.db.commit()

    for d in frappe.db.get_list("Journal Entry"):
        doc = frappe.get_doc("Journal Entry", d.name).delete()
    frappe.db.commit()

    # Payment Entry
    for d in frappe.db.get_list("Payment Entry", filters={"docstatus": 1}):
        frappe.get_doc("Payment Entry", d["name"]).cancel()
    frappe.db.commit()

    for d in frappe.db.get_list("Payment Entry"):
        doc = frappe.get_doc("Payment Entry", d.name).delete()
    frappe.db.commit()

    # # Item
    for d in frappe.db.get_list("Item"):
        doc = frappe.get_doc("Item", d.name).delete()
    frappe.db.commit()

    # # Booking
    for d in frappe.db.get_list("Accommodation Booking"):
        frappe.get_doc("Accommodation Booking", d["name"]).delete()
    frappe.db.commit()


def pivot_to_report(pivot):
    columns = [
        dict(label=d, fieldname=d, fieldtype="Varchar", width=120)
        for d in pivot.index.names
    ]
    columns = columns + \
        [dict(label=c, fieldname=c, fieldtype="Int", width=90)
            for c in pivot.columns]
    from frappe.utils.csvutils import read_csv_content
    csv = read_csv_content(pivot.to_csv())
    return columns, csv[1:]