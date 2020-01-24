# -*- coding: utf-8 -*-
# Copyright (c) 2019, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class AccommodationPackagePricingItem(Document):

    def add_or_update_item(self):
        items = [frappe._dict({"item_code": "%s %s" % (self.package, self.room_type), "rate": self.rate}),
                 frappe._dict({"item_code": "%s %s Extra Bed" % (self.package, self.room_type), "rate": self.extra_bed_rate})]

        def create_item(item_code, rate):
            frappe.get_doc({
                "doctype": "Item",
                "item_code":  item_code,
                "item_name": item_code,
                "description": item_code,
                "item_group": "Services",
                "standard_rate": rate,
                "is_stock_item": 0,
                "is_purchase_item": 0,
                "sales_uom": "Nos",
            }).insert()

        for i in items:
            if not frappe.db.exists("Item", i["item_code"]):
                create_item(i["item_code"], i["rate"])
            else:
                doc = frappe.get_doc("Item", i["item_code"])
                doc.update({"standard_rate": i["rate"]})
                doc.save()
