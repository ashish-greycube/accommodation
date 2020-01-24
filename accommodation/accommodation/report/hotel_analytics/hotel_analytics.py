# Copyright (c) 2013, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	if not filters: filters = {}
	filters.update({"check_in": filters.get("date_range") and filters.get("date_range")[0], "check_out": filters.get("date_range") and filters.get("date_range")[1]})
	columns, data = get_data(filters)
	return columns, data

def get_columns(filters):
	pass

def get_data(filters):
	query = """
		SELECT  hrri.check_in,
		hr.room_type,
		hrri.room,
		sum(hrri.amount) revenue
		FROM `tabAccommodation Booking` hrr 
		INNER JOIN `tabAccommodation Booking Item` hrri ON hrri.parent = hrr.name
		LEFT OUTER JOIN `tabAccommodation Room` hr ON hrri.room = hr.name 
		where hrri.check_in BETWEEN '{check_in}' AND '{check_out}'
		GROUP BY hrri.check_in, hr.room_type, hrri.room
		ORDER BY hrri.check_in, hrri.room_type, hrri.room
		""".format(check_in = filters.get("check_in"), check_out = filters.get("check_out"))
	data = frappe.db.sql(query, filters, as_list=1)
	import pandas
	df=pandas.DataFrame(data, columns=["check_in", "room_type", "room", "revenue"])
	df["revenue"] = map(float, df["revenue"])
	index = []
	for key in filters:
		if key in ['room_type','room'] and filters.get(key) == 1:
			index.append(key)
	if not len(index) or len(data) == 0:
		return [[],[]]
	values = "revenue"
	
	pivot = pandas.pivot_table(df, index=index, columns=["check_in"], values=values, fill_value=0
				,aggfunc='sum', margins=True, margins_name='Total')
	return to_array(pivot)

def to_array(pivot):
    columns = [ dict(label=("Room No." if d == "room" else 
							"Room Type" if d == "room_type"	else d),
					fieldname=d,fieldtype="Data",
					width=(80 if d == "room" else 100)) for d in pivot.index.names]
    columns = columns + [dict(label=c, fieldname=c, fieldtype="Currency", width=90) for c in pivot.columns]
    # data = [[l for l in pivot.index[idx]]+([i for i in d])  for idx,d in enumerate(pivot.values)]
    from frappe.utils.csvutils import read_csv_content
    csv = read_csv_content(pivot.to_csv())
    return columns, csv[1:]