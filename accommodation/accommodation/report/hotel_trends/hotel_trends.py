# Copyright (c) 2013, DBF and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
    report = filters.get("report")
    if report == "Room Type Occupancy":
        columns, data = get_room_type_occupancy(filters)
    if report == "Room Occupancy":
        columns, data = get_room_occupancy(filters)

    return columns, data


def get_room_type_occupancy(filters):

    query = """
select
    d.db_date, room.room_type, coalesce(sum(if(r.room is null,0,1)),0) occ
from 
    tabDate d
cross join 
    `tabAccommodation Room` room 
left outer join 
    `tabAccommodation Booking Item` r on d.db_date between r.check_in and r.check_out  and room.name = r.room
where 
    d.db_date between %(check_in)s and %(check_out)s
    and r.item_status <> 'Cancelled'
group by 
    d.db_date, room.room_type
"""
    data = frappe.db.sql(query, filters, as_list=1)

    import pandas as pd
    df = pd.DataFrame(data, columns=['date', 'room_type', 'occ'])
    pivot = pd.pivot_table(df, index=['room_type'], columns=[
        'date'], values='occ', aggfunc=sum, margins=True, margins_name='Total', fill_value=0, dropna=True)

    from accommodation.accommodation import pivot_to_report
    return pivot_to_report(pivot)

def get_room_occupancy(filters):

    query = """
select
    d.db_date, room.room_type, room.name, coalesce(sum(if(r.room is null,0,1))) occ
from 
    tabDate d
cross join 
    `tabAccommodation Room` room 
left outer join 
    `tabAccommodation Booking Item` r on d.db_date between r.check_in and r.check_out  and room.name = r.room
where 
    d.db_date between %(check_in)s and %(check_out)s
    and r.item_status <> 'Cancelled'
group by 
    d.db_date, room.room_type, room.name
"""
    data = frappe.db.sql(query, filters, as_list=1)

    import pandas as pd
    df = pd.DataFrame(data, columns=['date', 'room_type', 'room', 'occ'])
    pivot = pd.pivot_table(df, index=['room_type', 'room'], columns=[
        'date'], values='occ', aggfunc=sum, margins=True, margins_name='Total', fill_value=0, dropna=True)

    from accommodation.accommodation import pivot_to_report
    return pivot_to_report(pivot)