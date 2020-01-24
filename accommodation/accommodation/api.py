# -*- coding: utf-8 -*-
# Copyright (c) 2019, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr
import requests
import json
import os
import pymssql

ASIM_SERVICE_API_URL = "http://api.dadabhagwan.org/AsimServices/api/Member/GetICardDetailsforJJ"


def db(database):
    def get_db_config(database):
        config = {}
        db_config = os.path.join(frappe.local.site_path,
                                 ".".join([database, 'json']))
        if os.path.exists(db_config):
            config.update(frappe.get_file_json(db_config))
        return config

    cfg = frappe._dict(get_db_config(database))
    if not cfg:
        raise Exception("Database '%s' not configured for syncing." % database)
    return pymssql.connect(cfg.server, cfg.user, cfg.passwd, cfg.db_name)


@frappe.whitelist()
def get_mahatma(**args):
    args.pop('cmd', None)
    filters = args
    where_conditions = []
    for d in filters:
        where_conditions.append(" {} like '%{}%'".format(d, filters[d]))
    where_conditions = " where " + " and ".join(
        where_conditions) if where_conditions else ""
    if where_conditions:
        with db('asimservice') as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute(
                    "select top 100 *, datediff(year,dob,getdate()) age from dbo.fnc_utara_getdata_icard() {}"
                    .format(where_conditions or ""))
                return [d for d in cursor]
    return []


# @frappe.whitelist()
# def fetch_icard(mahatma_id):
#     return dict(
#         first_name="Vijaya",
#         middle_name="Walaja",
#         last_name="Raghavan",
#         mobile_no="9000090000",
#         address1="B12 Sadhana",
#         address2="ATPL",
#         address3="Trimandir",
#         city="Gandhinagar",
#         state="Gujarat",
#         country="India",
#         email="vijay_wm@yahoo.com",
#         dob="1972-09-05")


@frappe.whitelist()
def fetch_icard(doc):
    doc = frappe.get_doc(json.loads(doc))
    try:
        r = requests.post(
            ASIM_SERVICE_API_URL, data={"ICardId": doc.mahatma_id})
        data = r.json()["result"][0]
        doc.update(data)
        return doc.as_dict()
    except Exception as e:
        return cstr(e)
