# -*- coding: utf-8 -*-
# Copyright (c) 2019, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe.model.document import Document


class AccommodationRoom(Document):
    def validate(self):
        if not self.company:
            self.company = erpnext.get_defaut_company()

