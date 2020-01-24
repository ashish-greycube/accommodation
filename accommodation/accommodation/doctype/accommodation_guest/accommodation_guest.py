# -*- coding: utf-8 -*-
# Copyright (c) 2019, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class AccommodationGuest(Document):
    def validate(self):
        self.full_name = "%s %s %s" % (
            self.first_name, self.middle_name[0] if self.middle_name else "", self.last_name)
        if not self.customer:
            self.customer = frappe.db.get_single_value(
                'Accommodation Settings', 'default_customer')
        if not self.customer:
            frappe.throw(
                "Default customer is not set in Accommodation Settings.")
