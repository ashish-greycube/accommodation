# -*- coding: utf-8 -*-
# Copyright (c) 2019, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.naming import make_autoname
import erpnext
from frappe.utils import date_diff, now_datetime, getdate, cint, flt, fmt_money
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import get_account_currency
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry, get_company_defaults
from erpnext.accounts.doctype.journal_entry.journal_entry import get_payment_entry_against_invoice

from frappe.utils import random_string


class AccommodationBooking(Document):
    def on_trash(self):
        # some checks or notification and logging ?
        pass

    def autoname(self):
        company = frappe.defaults.get_user_default(
            'company', user=frappe.session.user)
        abbr = frappe.db.get_value('Company', company, 'abbr')
        self.name = make_autoname("BK-{}-.YY.MM.DD.-.#".format(abbr))

    def validate(self):
        if self.status == 'Cancelled':
            frappe.msgprint(
                _("Cannot modify 'Cancelled' booking"), raise_exception=1)
            self.reload()

        if self.status == 'Booked':
            if [d.name for d in self.items if d.item_status == "Checked In"]:
                self.status = "Checked In"
                self.checked_in = now_datetime()
        elif self.status == 'Checked In':
            if not [
                    d.name for d in self.items
                    if d.item_status in ["Checked In", "Reserved"]
            ]:
                self.status = "Checked Out"
                self.checked_out = now_datetime()

        self.update_room_status()
        self.set_customer()
        self.set_allotted_beds()
        self.set_defaults()

    def set_defaults(self):
        if not self.company:
            self.company = frappe.defaults.get_user_default(
                'company', user=frappe.session.user)

    def set_allotted_beds(self):
        for d in [i for i in self.items if i.room and i.alloted_beds]:
            # remove deleted beds
            frappe.db.sql(
                """
            update `tabAccommodation Room Bed` set booking = null
            where booking = %s and parent=%s and bed_number not in ({})
            """.format(d.alloted_beds), (self.name, d.room))
            # add allotted beds
            frappe.db.sql(
                """
            update `tabAccommodation Room Bed` set booking = %s where parent=%s and bed_number in ({})
            """.format(d.alloted_beds), (self.name, d.room))

    def update_room_status(self):
        def _set_room_status(room_status, rooms=[]):
            if rooms:
                frappe.db.sql(
                    """update `tabAccommodation Room`
                    set room_status= %s
                    where name in (%s)
                """, (room_status, ",".join(rooms)))

        # room status transitions
        for d in [r for r in self.items if r.room]:
            if d.get("__islocal", 0):
                if d.item_status == "Checked In":
                    _set_room_status('Occupied', [d.room])
                continue
            # existing line
            for db_doc in frappe.db.get_values(
                    d.doctype, d.name, ['room', 'item_status'], as_dict=1):
                # handle transitions
                if d.room == db_doc.room:
                    # no status change
                    if d.item_status == db_doc.item_status:
                        continue
                    # 'Reserved' --> 'Checked In'
                    elif d.item_status == 'Checked In':
                        _set_room_status('Occupied', [d.room])
                    # 'Checked In' --> 'Checked Out' or 'Cancelled'
                    elif db_doc.item_status == "Checked In":
                        _set_room_status('Dirty', [d.room])
                else:
                    # room transfer: set old room to 'Dirty'
                    if db_doc.item_status == "Checked In":
                        _set_room_status('Dirty', [db_doc.room])

    def set_customer(self):
        if not self.customer:
            customer = frappe.db.get_value("Accommodation Guest", self.guest,
                                           "customer")
            self.customer = customer or frappe.db.get_single_value(
                'Accommodation Settings', 'default_customer')
        if not self.customer_group or self.customer != self.get_db_value(
                "customer"):
            self.customer_group = frappe.db.get_value(
                "Customer", self.customer, "customer_group")

    def set_item_rates(self):
        self.total_amount = 0
        for d in self.items:
            if d.room:
                d.room_count = 1
            if d.room_type and d.check_in and d.check_out:
                rates = get_package_rates(self.package, d.room_type,
                                          d.check_in, d.check_out)
                d.room_rate = rates["rate"]
                d.bed_rate = rates["extra_bed_rate"]
                num_days = date_diff(d.check_out, d.check_in) or 1
                d.amount = (d.total_extra_bed_count * d.bed_rate)
                if not cint(
                        frappe.db.get_value('Accommodation Package',
                                            self.package, 'is_shared')):
                    d.amount = ((d.room_count * num_days * d.room_rate) + (
                        d.total_extra_bed_count * num_days * d.bed_rate))
                self.total_amount += d.amount

    def cancel_sales_invoice(self):
        si = self.invoice
        if si:
            self.db_set("invoice", None)
            doc = frappe.get_doc("Sales Invoice", si)
            if doc.docstatus == 1:
                doc.cancel()
            frappe.delete_doc("Sales Invoice", si)

    def submit_sales_invoice(self):
        if self.invoice:
            doc = frappe.get_doc("Sales Invoice", self.invoice)
            if doc.docstatus == 0:
                doc.submit()

    def set_advances(self, si_doc):
        """Adjusts advances against Booking"""
        advance_entries = frappe.db.sql(
            """
        select
            "Journal Entry" as reference_type, t1.name as reference_name,
            t1.remark as remarks, t2.credit_in_account_currency as amount, t2.name as reference_row,
            t2.reference_name as against_order
        from
            `tabJournal Entry` t1, `tabJournal Entry Account` t2
        where
            t1.name = t2.parent and t2.account = %s
            and t2.party_type = 'Customer' and t2.party = %s
            and t2.is_advance = 'Yes' and t1.docstatus = 1
            and credit_in_account_currency > 0
            and ifnull(t2.reference_name, '')=''
            and t1.accommodation_booking = %s
        order by t1.posting_date
        """, (si_doc.debit_to, si_doc.customer, self.name),
            as_dict=True)

        advance_allocated = 0
        for d in advance_entries:
            if d.against_order:
                allocated_amount = flt(d.amount)
            else:
                amount = si_doc.rounded_total or si_doc.grand_total
                allocated_amount = min(amount - advance_allocated, d.amount)
            advance_allocated += flt(allocated_amount)

            si_doc.append(
                "advances", {
                    "doctype": si_doc.doctype + " Advance",
                    "reference_type": d.reference_type,
                    "reference_name": d.reference_name,
                    "reference_row": d.reference_row,
                    "remarks": d.remarks,
                    "advance_amount": flt(d.amount),
                    "allocated_amount": allocated_amount
                })

    def make_sales_invoice(self, submit_invoice=1):

        si = frappe.get_doc({
            "doctype":
            "Sales Invoice",
            "company":
            self.company,
            "posting_date":
            getdate(),
            "due_date":
            getdate() + relativedelta(days=7),
            "customer":
            self.customer,
            "customer_name":
            self.customer_contact
            if self.customer_group == "Internal" else None
        })

        line_items = frappe.db.sql(
            """
        select
t.item_code, t.days acc_room_days, t.room_count acc_room_count, if(t.days<2,1,t.days)*t.room_count qty
from
(
    select
    concat(b.package, ' ', bi.room_type) item_code,
    timestampdiff(day,bi.check_in, bi.check_out) days,
    sum(room_count) room_count
    from
        `tabAccommodation Booking` b
    inner join `tabAccommodation Booking Item` bi on bi.parent = b.name
    where b.name=%s
    group by b.name, concat(b.package, ' ', bi.room_type), timestampdiff(day,bi.check_in, bi.check_out)
) t
union all
select
t.item_code, 0 days, 0 room_count, t.qty
from
(
    select
    concat(b.package, ' ', bi.room_type, ' Extra Bed') item_code,
    count(room_count) room_count,
    sum(total_extra_bed_count) qty
    from
        `tabAccommodation Booking` b
    inner join `tabAccommodation Booking Item` bi on bi.parent = b.name and bi.total_extra_bed_count > 0
    where b.name=%s
    group by b.name, concat(b.package, ' ', bi.room_type)
) t
        """, (self.name, self.name),
            as_dict=1)
        for d in line_items:
            si.append("items", d)
        si.set_missing_values()
        si.insert()

        frappe.db.set_value("Accommodation Booking", self.name, 'invoice',
                            si.name)
        frappe.db.commit()

        self.set_advances(si)
        balance = si.outstanding_amount
        for d in si.advances:
            if balance > 0:
                d.allocated_amount = d.advance_amount if (
                    balance > d.advance_amount) else balance
                balance -= d.allocated_amount

        if cint(submit_invoice):
            si.submit()
        else:
            si.save()

        if self.customer_group == "Internal ":
            # Auto settle Internal customer payments
            from accommodation.accommodation.controller import make_payment
            make_payment(
                booking=self.name,
                amount=si.rounded_total,
                posting_date=si.posting_date,
                mode_of_payment="Internal")
            frappe.msgprint(
                _("Created Invoice {0} and payment settled.").format(si.name),
                alert=True)

    def set_payment_status(self):
        if self.invoice:
            details = frappe.db.get_values(
                "Sales Invoice",
                self.invoice, ['total_advance', 'outstanding_amount'],
                as_dict=1)
            if not details.outstanding_amount:
                self.payment_status = "Paid"
            elif details.total_advance and details.total_advance > 0:
                self.payment_status = "Advance Paid"
        elif frappe.db.sql(
                """select 1 from `tabJournal Entry` where remark like '%{} '"""
                .format(self.name)):
            self.payment_status = "Advance Paid"
        else:
            self.payment_status = "Unpaid"

    def get_print_doc(self):
        print_doc = self.get_receipt_print()
        print_doc.purpose_of_visit = _(
            "For attending Satsang.") if self.package in [
                "Mahatma", "Member", "Sharing", "MHT"
            ] else _("For temple visit.")
        print_doc.room_items = []
        room_items = frappe.db.sql(
            """
select
    replace(si.item_name, bkg.package, '') particulars,
    nullif(si.acc_room_days,0) days,
    nullif(si.acc_room_count,0) room_count,
    cast(si.qty as int) qty,
    si.rate,
    si.amount
from
    `tabAccommodation Booking` bkg
inner join `tabSales Invoice Item` si on
    si.parent = bkg.invoice
where bkg.name=%s
order by si.idx
            """, (self.name),
            as_dict=1)
        print_doc.room_items = [d for d in room_items]
        return print_doc

    def get_receipt_print(self):
        doc = frappe.db.get_values(
            "Accommodation Guest",
            self.guest, [
                'mobile_no', 'full_name', 'address_1', 'address_2', 'city',
                'state', 'country'
            ],
            as_dict=1)
        doc = doc[0] if doc else frappe._dict()
        rooms = ([d.room for d in self.items])
        rooms = ", ".join(
            rooms) if len(rooms) < 4 else "%d rooms" % (len(rooms), )

        doc.update({
            'name':
            self.name,
            'checked_in':
            self.checked_in,
            'checked_out':
            self.checked_out,
            'pax':
            self.person,
            'rooms':
            rooms,
            'address':
            "{0} {1}\n{2},{3},{4}".format(doc.address_1 or "", doc.address_2
                                          or "", doc.city or "", doc.state
                                          or "", doc.country or ""),
            'remarks':
            self.remarks
        })
        return doc


def get_package_rates(package, room_type, from_date, to_date):
    data = frappe.db.sql(
        """
        select ppi.package, ppi.rate, ppi.extra_bed_rate
        from `tabAccommodation Package Pricing` pp
        inner JOIN `tabAccommodation Package Pricing Item` ppi on ppi.parent = pp.name
        and ppi.package= %s and ppi.room_type = %s
        where pp.start_date <= %s and pp.end_date >= %s
        """, (package, room_type, from_date, to_date),
        debug=0,
        as_dict=1)
    if not data:
        frappe.msgprint(
            "'%s' package rates not set for room type '%s'" %
            (frappe.bold(package), frappe.bold(room_type)),
            title='Error',
            indicator='red',
            raise_exception=1)
    elif len(data) > 1:
        frappe.msgprint(
            "'%s' package multiple rates found for room type '%s'" %
            (frappe.bold(package), frappe.bold(room_type)),
            title='Error',
            indicator='red',
            raise_exception=1)
    return data[0]
