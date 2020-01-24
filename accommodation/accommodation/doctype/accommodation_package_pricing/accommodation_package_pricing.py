# -*- coding: utf-8 -*-
# Copyright (c) 2019, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, date_diff
from frappe.model.document import Document


class AccommodationPackagePricing(Document):
    def validate(self):
        self.validate_date_range()
        for d in self.items:
            d.add_or_update_item()

    def validate_date_range(self):
        for d in frappe.db.get_list(
                "Accommodation Package Pricing",
                fields=['name', 'start_date', 'end_date', 'company'],
                filters=[['company', '=', self.company]]):
            if not self.name == d.name and not (
                    date_diff(self.end_date, d.start_date) < 0
                    or date_diff(self.start_date, d.end_date) > 0):
                frappe.throw(
                    "Pricing Package %s already exists for date range %s to %s."
                    % (d.name, d.start_date, d.end_date))
