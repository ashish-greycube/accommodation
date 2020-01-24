# -*- coding: utf-8 -*-
# Copyright (c) 2019, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from six import string_types, iteritems
import json
import erpnext
from frappe.utils import date_diff, now_datetime, getdate, cint, flt, fmt_money, add_days
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import get_account_currency
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry, get_company_defaults
from erpnext.accounts.doctype.journal_entry.journal_entry import get_payment_entry_against_invoice
from PyPDF2 import PdfFileWriter, PdfFileReader


def write_to_local(content):
    import os
    from frappe.utils.file_manager import get_random_filename
    public_files = frappe.get_site_path('public', 'files')
    fname = get_random_filename(extn=".pdf")
    with open(os.path.join(public_files, fname), "w") as f:
        f.write(content)


def get_invoice_summary_html(invoices=[]):
    '''aggregated summary of all invoices'''
    if not invoices:
        return ""

    doc_list = frappe.db.get_all('Sales Invoice', {"name": ["in", invoices]}, [
        'posting_date', 'name', 'company', 'customer', 'customer_name',
        'remarks', 'rounded_total'
    ])

    from datetime import datetime

    month = ",".join(
        list(
            set([datetime.strftime(d.posting_date, '%b %Y')
                 for d in doc_list])))
    title, company = "", ""
    for invoice in doc_list:
        company = invoice.company
        header_title = "{0} - Internal Vouchers for {1} {2}".format(
            invoice.company, invoice.customer, month)
        break

    template = "accommodation/templates/emails/internal_voucher_summary.html"
    args = {
        "company": company,
        "date": getdate(),
        "header_title": header_title,
        "invoices": doc_list,
    }
    return frappe.render_template(template, {"doc": args}), header_title


def get_invoice_as_attachments(invoices, print_format="Sales Invoice SNS"):
    # print_format = frappe.db.get_single_value("Delivery Settings", "dispatch_attachment")
    attachments = []
    for invoice in invoices:
        attachments.append(
            frappe.attach_print(
                "Sales Invoice",
                invoice,
                file_name="Internal Voucher - %s" % invoice,
                print_format=print_format))
    return attachments


def get_invoice_merged(invoices, print_format="Sales Invoice SNS"):
    invoices = ['SINV-SNS-190227-1', 'SINV-SNS-190227-3']
    # print_format = frappe.db.get_single_value("Delivery Settings", "dispatch_attachment")
    attachments = []
    from PyPDF2 import PdfFileWriter, PdfFileReader
    output = PdfFileWriter()
    for invoice in invoices:
        output = frappe.get_print(
            "Sales Invoice", invoice, print_format, as_pdf=True, output=output)
    from frappe.utils.print_format import read_multi_pdf

    return [{
        "fname": "Internal Voucher.pdf",
        "fcontent": read_multi_pdf(output)
    }]


@frappe.whitelist()
def send_internal_invoice_emails(invoices=None):
    if not invoices:
        return
    if isinstance(invoices, string_types):
        invoices = json.loads(invoices)

    for group in get_invoice_email_groups(invoices=invoices):
        doc_list = [d for d in group.invoices.split(",")]
        message, title = get_invoice_summary_html(doc_list)
        attachments = get_invoice_merged(doc_list)
        attachments[0]["fname"] = "%s.pdf" % title

        recipients = [group.to]
        cc = group.cc.split("\n") if group.cc else []
        bcc = []

        # from frappe.utils.background_jobs import enqueue
        # enqueue(
        #     method=frappe.sendmail,
        #     queue='short',
        #     timeout=300,
        #     now=True,
        #     is_async=False,
        #     attachments=attachments,
        #     subject=title,
        #     message=message,
        #     recipients=recipients,
        #     cc=cc,
        #     bcc=bcc)

        frappe.sendmail(
            recipients=recipients,
            message=message,
            subject=title,
            attachments=attachments)


def get_invoice_email_groups(invoices=None):
    if not invoices:
        return []
    where = " where si.name in ('%s')" % "','".join(invoices)

    return frappe.db.sql(
        """
    select
	group_concat(si.name) invoices,
	ct.email_id `to`,
	cus.customer_details `cc`
from
	`tabSales Invoice` si
inner join `tabAccommodation Booking` ab on
	ab.invoice = si.name
left outer join `tabContact` ct on
	ct.name = ab.customer_contact
left outer join tabCustomer cus on
	cus.name = si.customer
    {}
group by
	ab.customer,
	si.customer_name,
	ab.customer_contact,
	ct.email_id,
	cus.customer_details
    """.format(where),
        as_dict=1)
