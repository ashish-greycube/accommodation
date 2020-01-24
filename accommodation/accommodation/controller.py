# -*- coding: utf-8 -*-
# Copyright (c) 2019, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, nowdate
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


@frappe.whitelist()
def set_item_rates(booking):
    """Calculate rate for each day as it may belong to different Hotel Room Pricing Item"""
    doc = frappe.get_doc(json.loads(booking))
    doc.set_item_rates()
    return doc.as_dict()


@frappe.whitelist()
def get_payments_for_booking(booking):
    """Journal Entry lines for Booking"""
    return frappe.db.sql(
        """
    select je.name, je.posting_date, je.total_amount, je.total_amount_currency, je.owner, je.pay_to_recd_from,
    case when jea.credit > 0 then 1 else 0 end is_refund
    from `tabJournal Entry` je
    inner join `tabAccommodation Booking` ab on ab.name = je.accommodation_booking
    inner join `tabJournal Entry Account` jea on jea.parent = je.name and jea.against_account = ab.customer
    where coalesce(je.accommodation_booking,'')=%s and je.docstatus=1
    """, (booking),
        as_dict=1)


@frappe.whitelist()
def get_available_rooms(doctype, txt, searchfield, start, page_len, filters):
    args = dict(
        txt=frappe.db.escape(txt),
        package=filters.get('package', ''),
        room_type=filters.get('room_type', ''),
        from_date=filters.get('check_in', ''),
        to_date=filters.get('check_out', ''),
    )

    return frappe.db.sql(
        """
            select
                distinct(ar.name) name
            from
                `tabAccommodation Room` ar
            left outer join `tabAccommodation Booking Item` abi on
                abi.room = ar.name
                and (abi.item_status = 'Checked In' or abi.item_status = 'Reserved')
                and not (abi.check_out <= '{from_date}'
                or abi.check_in >= '{to_date}')
            where
                ar.room_status <> 'Maintenance'
                and ifnull(ar.room_status,'') != 'Dirty'
                and abi.room is null
                and ar.name like concat('%','{txt}','%')
                and ar.room_type = '{room_type}'
            union all
            select
                distinct(abi.room) name
            from
                `tabAccommodation Booking` ab
            inner join `tabAccommodation Booking Item` abi on
                abi.parent = ab.name
                and abi.room is not null
            inner join `tabAccommodation Package` pck on pck.name = ab.package and pck.is_shared=1
            where
                abi.item_status = 'Checked In' and pck.name = '{package}'
            order by name
    """.format(**args),
        debug=0)


@frappe.whitelist()
def get_customer_contacts(customer):
    data = frappe.db.sql(
        """select parent from `tabDynamic Link` where link_doctype = 'Customer'
            and parenttype = 'Contact' and link_name = %s""", (customer, ))
    if not data:
        frappe.msgprint(
            "No contacts found for customer '%s'" % frappe.bold(customer),
            title='Error',
            indicator='red',
            raise_exception=1)
    return list(data)


@frappe.whitelist()
def get_frontdesk(from_date, to_date):
    # alternate query
    # select
    # 	cal.db_date,
    # 	r.name,
    # 	trim( ',' from concat_ws(',', case r.room_status when 'Dirty' then 'DT' when 'Occupied' then '' when 'Maintenance' then 'MT' else '' end, case bi.item_status when 'Checked In' then case when bi.check_out = cal.db_date then 'CO' else 'CI' end when 'Reserved' then 'RS' else '' end)) status,
    # 	bi.parent booking
    # from
    # 	`tabAccommodation Room` r
    # cross join tabDate cal
    # left outer join `tabAccommodation Booking Item` bi on
    # 	bi.room = r.name
    # 	and (bi.check_in <= cal.db_date
    # 	and bi.check_out >= cal.db_date)
    # 	and bi.item_status in ('Checked In',
    # 	'Reserved')
    # where cal.db_date >= %(from_date)s and cal.db_date <= %(to_date)s
    # order by
    # 	cal.db_date,
    # 	r.room_type,
    # 	r.name
    company = frappe.defaults.get_user_default(
        'company', user=frappe.session.user)
    data = frappe.db.sql(
        """
        select r.name, r.room_type, cal.db_date,
        concat_ws('/', replace(lower(bk.item_status),' ','_'), bk.name, bk.guest_name) description
        from `tabAccommodation Room` r
        cross join tabDate cal
        left outer JOIN
        (
            -- Checked In/Reserved/Cleaning for available rooms
            select ab.name, concat_ws(' ',gu.first_name, gu.last_name) guest_name,
            abi.item_status, ab.package, coalesce(abi.room,'') room, abi.check_in, abi.check_out
            from `tabAccommodation Booking` ab
            inner join  `tabAccommodation Booking Item` abi on abi.parent = ab.name and abi.room is not null
            inner join `tabAccommodation Guest` gu on gu.name = ab.guest
            where (abi.item_status = 'Checked In' or abi.item_status = 'Reserved')
        ) bk on bk.room = r.name and cal.db_date >= bk.check_in and cal.db_date <= bk.check_out
        where
        r.room_status <> 'Maintenance'
        and cal.db_date >= %(from_date)s and cal.db_date <= %(to_date)s and r.company = %(company)s
        order by r.room_type, r.name
    """, {
            'from_date': from_date,
            'to_date': to_date,
            'company': company
        },
        as_list=1,
        debug=0)

    import pandas as pd
    df = pd.DataFrame(
        data, columns=['room', 'room_type', 'date', 'description'])
    pivot = pd.pivot_table(
        df,
        fill_value='',
        dropna=True,
        index=['room_type', 'room'],
        columns=['date'],
        values=['description'],
        aggfunc=lambda x: ' '.join(str(v) for v in x))
    #    aggfunc=sum, margins=True, margins_name='Total', fill_value=0, dropna=True)

    columns = ["room_type", "room"] + \
        [d[1].strftime('%b_%d').lower() for d in pivot.columns]

    result = []
    for d in pivot.to_records():
        result.append(dict(zip(columns, d)))

    return columns, result


@frappe.whitelist()
def set_cleaned(rooms):
    rooms = list(json.loads(rooms or "[]"))
    for d in rooms:
        frappe.db.set_value(
            "Accommodation Room", d, "room_status", "Clean", update_modified=1)


@frappe.whitelist()
def get_room_management(filters):
    filters = json.loads(filters) if filters else dict()
    conditions = []
    conditions += [
        "company = '%s'" % frappe.defaults.get_user_default(
            'company', user=frappe.session.user)
    ]
    if filters.get("room_status", None):
        conditions += [
            " room_status = '{}'".format(filters.get("room_status"))
        ]
    if filters.get("room_type", None):
        conditions += [" room_type = '{}'".format(filters.get("room_type"))]
    conditions = " where " + " and ".join(conditions) if conditions else ""
    data = frappe.db.sql(
        """
    select
        name,
        room_type,
        room_status
    from
        `tabAccommodation Room`
        {}
    """.format(conditions),
        as_dict=1)

    return {"columns": [], "data": data}


@frappe.whitelist()
def get_beds(room, booking):
    beds = frappe.db.sql(
        """
        select case
        when booking is null then ''
        when booking = %s then 'X'
        else 'O'
        end
        from `tabAccommodation Room Bed` where parent=%s
        order by bed_number""", (booking, room))
    return [[d[0] for d in beds]] if beds else [[]]


def check_outstanding(invoice, amount):
    company = frappe.defaults.get_user_default(
        'company', user=frappe.session.user)
    currency = erpnext.get_company_currency(company)
    outstanding_amount = flt(
        frappe.db.get_value("Sales Invoice", invoice, "outstanding_amount"))
    if amount > outstanding_amount:
        frappe.throw(
            _("Payment exceeds the outstanding amount of %s" % (frappe.bold(
                fmt_money(outstanding_amount, currency=currency)), )),
            title="Over Payment of Invoice")


@frappe.whitelist()
def make_payment(booking,
                 amount,
                 posting_date,
                 mode_of_payment='Cash',
                 is_refund=0,
                 cheque_no=None,
                 cheque_date=None,
                 submit=True):
    is_refund = cint(is_refund)

    from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
    company = frappe.defaults.get_user_default(
        'company', user=frappe.session.user)
    cost_center = frappe.db.get_value('Company', company, 'cost_center')
    bank_cash_account = get_bank_cash_account(mode_of_payment, company)
    receivable_payable_account = frappe.db.get_value(
        "Company", company, "default_receivable_account")
    amount = flt(amount)
    remark = 'Payment received against Booking %s' % (
        booking) if not is_refund else 'Deposit refund against Booking %s' % (
            booking)

    booking_doc = frappe.db.get_values(
        "Accommodation Booking", {"name": booking}, [
            'invoice', 'customer', 'customer_group', 'customer_contact',
            'invoice_amount', 'outstanding_amount', 'advance_amount'
        ],
        as_dict=1)[0]
    invoice = booking_doc.get('invoice', None)
    customer = booking_doc.get('customer', None)
    customer_contact = booking_doc.get('customer_contact', None)
    is_advance = "No" if is_refund or invoice else "Yes"
    if booking_doc.get('customer_group', None) == "Internal":
        remark = _("Internal Voucher for {0} instructed by {1}").format(
            customer, customer_contact)

    journal_entry_to_adjust = get_journal_entry_to_adjust(
        company, customer, amount) if is_refund else None

    if not is_refund and invoice:
        check_outstanding(invoice, amount)

    if mode_of_payment == "Internal Voucher":
        cheque_date = posting_date
        cheque_no = customer_contact

    je = frappe.get_doc({
        "doctype":
        "Journal Entry",
        "voucher_type":
        "Cash Entry" if mode_of_payment == "Cash" else "Bank Entry",
        "posting_date":
        posting_date,
        "company":
        company,
        "remark":
        remark,
        "accommodation_booking":
        booking,
        "cheque_date":
        cheque_date,
        "cheque_no":
        cheque_no
    })

    je.set(
        "accounts",
        [{
            "account": bank_cash_account.get("account"),
            "cost_center": cost_center,
            "debit_in_account_currency": amount if not is_refund else 0,
            "credit_in_account_currency": amount if is_refund else 0,
            "is_advance": is_advance,
        },
         {
             "cost_center": cost_center,
             "account": receivable_payable_account,
             "party_type": "Customer",
             "party": customer,
             "debit_in_account_currency": amount if is_refund else 0,
             "credit_in_account_currency": amount if not is_refund else 0,
             "is_advance": is_advance,
             "reference_type":
             "Sales Invoice" if invoice and not is_refund else None,
             "reference_name": invoice if not is_refund else None
         }])

    je.insert(ignore_permissions=True)
    je.submit()

    # update_payment_status()

    if journal_entry_to_adjust:
        # Update payment JE with reference. Adjust against first unadjusted voucher with amount = refund amount
        voucher_no = journal_entry_to_adjust.reference_name
        entries = frappe.db.get_all(
            "Journal Entry Account",
            filters={
                "parent": voucher_no,
                "account": receivable_payable_account,
                "against_account": bank_cash_account
            })
        for d in entries:
            if not d.reference_type and not d.reference_name:
                frappe.db.set_value('Journal Entry Account', d.name,
                                    'reference_type', "Journal Entry")
                frappe.db.set_value('Journal Entry Account', d.name,
                                    'reference_name', je.name)
        entries = frappe.db.get_all(
            "GL Entry",
            filters={
                "voucher_type": "Journal Entry",
                "voucher_no": voucher_no,
                "party": customer
            })
        for d in entries:
            if not d.against_voucher_type and not d.against_voucher:
                frappe.db.set_value("GL Entry", d.name, "against_voucher_type",
                                    "Journal Entry")
                frappe.db.set_value("GL Entry", d.name, "against_voucher",
                                    je.name)

    advance = booking_doc.advance_amount + (amount
                                            if not is_refund else 0 - amount)
    outstanding = booking_doc.outstanding_amount + (amount if is_refund else
                                                    0 - amount)

    invoice_status = None if not invoice else frappe.db.get_value(
        "Sales Invoice", invoice, 'status')
    frappe.db.sql(
        """
    update `tabAccommodation Booking`
    set advance_amount = %s, outstanding_amount = %s, invoice_status = %s
    where name = %s""", (advance, outstanding, invoice_status, booking))

    # frappe.db.set_value(
    #     "Accommodation Booking",
    #     booking,
    #     "advance_amount",
    #     advance,
    #     update_modified=False)

    # frappe.db.set_value(
    #     "Accommodation Booking",
    #     booking,
    #     "outstanding_amount",
    #     outstanding,
    #     update_modified=False)

    frappe.db.commit()
    return je.name


def get_journal_entry_to_adjust(company, customer, refund_amount):
    receivable_payable_account = frappe.db.get_value(
        "Company", company, "default_receivable_account")
    doc = frappe.get_doc({
        "doctype":
        "Payment Reconciliation",
        "company":
        company,
        "party_type":
        "Customer",
        "party":
        customer,
        "receivable_payable_account":
        receivable_payable_account
    })
    doc.get_nonreconciled_payment_entries()
    entry = [d for d in doc.payments if d.amount == refund_amount]
    if not entry:
        frappe.throw(_("No payments found to refund."), title="Invalid refund")
    return entry[0]


@frappe.whitelist()
def get_internal_customer(doctype, txt, searchfield, start, page_len, filters):
    where_clause = [" customer_group = 'Internal' "]
    if not filters:
        filters = {}
    month = filters.get("month", None)

    if (month):
        where_clause.append("month(posting_date) = {}".format(month))

    where_clause = "where" + (
        " and ".join(where_clause)) if where_clause else ""

    return frappe.db.sql(
        """
    select
    customer
from
    `tabSales Invoice` {}""".format(where_clause),
        debug=0)


@frappe.whitelist()
def approve_all_internal_invoices(invoice_list, approval_date):
    # '''pay all Unpaid invoices for the customer, Payment Mode = Internal'''
    invoice_list = json.loads(invoice_list) if invoice_list else []
    doc_list = frappe.db.sql(
        """
    select
        bk.name, si.outstanding_amount
    from
        `tabAccommodation Booking` bk
        inner join `tabSales Invoice` si on si.name = bk.invoice
        and si.status = 'Unpaid'
        and si.outstanding_amount > 0
        and si.name in ({})
    """.format(",".join(["'%s'" % d for d in invoice_list])),
        as_dict=1)

    for d in doc_list:
        make_payment(
            d["name"],
            d["outstanding_amount"],
            posting_date=approval_date,
            mode_of_payment='Internal Voucher',
            is_refund=0,
            cheque_no=None,
            cheque_date=None,
            submit=True)


@frappe.whitelist()
def email_all_internal_invoices(invoice_list=None, format="Sales Invoice SNS"):
    invoice_list = json.loads(invoice_list) if invoice_list else []
    if not invoice_list: return

    data = frappe.db.sql(
        """select
    company,
    monthname(posting_date) month,
    customer,
    group_concat(name) invoices
from
    `tabSales Invoice`
where
    customer_group = 'Internal' and name in ({})
group by
    company, monthname(posting_date), customer
order by
    company, monthname(posting_date), customer
    """.format(",".join(["'%s'" % d for d in invoice_list])),
        as_dict=1)
    output = PdfFileWriter()
    from frappe.utils.print_format import read_multi_pdf
    from frappe.utils.pdf import get_pdf
    for d in data:
        invoices = ",".join(["'%s'" % m for m in d.invoices.split(",")])
        html = get_invoice_summary(invoices)
        output = get_pdf(html, output=output)
        for i in d.invoices.split(","):
            output = frappe.get_print(
                "Sales Invoice", i, format, as_pdf=True, output=output)
        send_customer_emails(d.company, d.customer, d.month, invoices,
                             read_multi_pdf(output))


def get_invoice_summary(invoices):
    invoices = frappe.db.sql(
        """
    select posting_date, name, company, monthname(posting_date) month, customer, customer_name, remarks, rounded_total
    from `tabSales Invoice`
    where name in ({})
    """.format(invoices),
        as_dict=1)
    if invoices:
        header_title = "{0} - Internal Vouchers for {1} in the month of {2}".format(
            invoices[0]["company"], invoices[0]["customer"],
            invoices[0]["month"])
        template = "accommodation/templates/emails/internal_voucher_summary.html"
        doc = {
            "invoices": invoices,
            "company": invoices[0]["company"],
            "date": getdate(),
            "header_title": header_title
        }
        return frappe.render_template(template, {"doc": doc})


def write_to_local(content):
    import os
    from frappe.utils.file_manager import get_random_filename
    public_files = frappe.get_site_path('public', 'files')
    fname = get_random_filename(extn=".pdf")
    with open(os.path.join(public_files, fname), "w") as f:
        f.write(content)


def get_invoice_as_attachments(invoices):
    # print_format = frappe.db.get_single_value("Delivery Settings", "dispatch_attachment")
    print_format = "Sales Invoice SNS"
    attachments = []
    for invoice in invoices:
        attachments.append(
            frappe.attach_print(
                "Sales Invoice",
                invoice,
                file_name="Internal Voucher - %s" % invoice,
                print_format=print_format))


def validate_employee(doc, method):
    # set default company for user (employee)
    if doc.user_id and doc.company:
        frappe.defaults.set_user_default(
            "company", doc.company, user=doc.user_id)


def autoname_sales_invoice(doc, method):
    abbr = frappe.db.get_value('Company', doc.company, 'abbr')
    from frappe.model.naming import make_autoname
    doc.name = make_autoname("SINV-{}-.YY.MM.DD.-.#".format(abbr))


def autoname_journal_entry(doc, method):
    abbr = frappe.db.get_value('Company', doc.company, 'abbr')
    from frappe.model.naming import make_autoname
    doc.name = make_autoname("JV-{}-.YY.MM.DD.-.#".format(abbr))


@frappe.whitelist()
def cancel_booking(name):
    frappe.db.sql(
        """update `tabAccommodation Booking` set status = %s, modified = %s
    where name=%s""", ('Cancelled', nowdate(), name))

    frappe.db.sql(
        """update `tabAccommodation Booking Item` set item_status = %s, modified = %s
    where parent=%s""", ('Cancelled', nowdate(), name))


def on_update_sales_invoice(doc, method):
    frappe.db.sql(
        """update `tabAccommodation Booking`
    set total_amount = %(rounded_total)s, invoice_amount = %(rounded_total)s ,
    outstanding_amount = (%(rounded_total)s - advance_amount),
    invoice_status = %(status)s
    where invoice = %(name)s """, {
            "rounded_total": flt(doc.rounded_total),
            "status": doc.status,
            "name": doc.name
        })
    # (flt(doc.rounded_total), flt(doc.rounded_total), doc.status, doc.name))


def on_trash_sales_invoice(doc, method):
    frappe.db.sql(
        """
    update `tabAccommodation Booking`
    set invoice = null, invoice_status = null
    where invoice = %s
    """, (doc.name, ))
