## Accommodation

A light weight Hotel Management system built on Frappe & Erpnext. Can manage rooms booking, check in, checkout and room management. Rooms are created as Erpnext items. Room types are mapped to packages and pricing is managed through a pricing package.

Invoicing uses the Erpnext 'Sales Invoice'. Payments is managed through 'Journal Entry'. Advances may be taken against booking, that are adjusted against invoice, when invoice is generated.

#### License

MIT

### System Setup

#### Administrator
- If Dates not created, create using make_data() (date.py) definition from bench console
- Change "Service" item to Group
- Create a Company for each unit e.g. Stop N Stay, Dormitory 
- Create services  e.g. Breakage Charge, Laundry Service if needed
- Administrator account cannot be used 

#### Accounts configuration
- set "Default Price List" = "Standard Selling" at Customer level
- Create a Bank Account for Internal Vouchers
- Create Mode Of Payment - "Internal Voucher", set default account company-wise to account created above. All internal vouchers will be paid into this account
- Create a Customer Group - "Internal". 
- Create a customer for each internal Department. 
- Create contacts in each customer for internal voucher approvers. Emails of vouchers will be sent to contact's email 
- Add emails - 1 per line in Customer > More Info > customer_details to be cc'ed in internal voucher emails for that Customer(department)

#### Accommodation Settings
- Default customer

#### User
- Create User for each Company and make them an employee of the company. 
- In User Permissions add entry for particular Company for each User. (Entities such as Room,Room Type,Bookings will be filtered by Company of User) 
- On creation of Employee, the default company of User is created, which is used in all transactions

#### Masters
    1. Accommodation Room Type
    2. Accommodation Room
    3. Accommodation Package
    4. Accommodation Package Pricing
    
#### Permissions

### User Manual

#### Status
- Booking Status - Reserved > Checked In > Checked Out
- Payment Status - Unpaid > Partial Paid > Paid
- Room Status > Reserved, Checked In, Checked Out
- Booking status changes from reserved to Checked In when first room is checked in.
- Booking status changes from 'Checked In' to 'Checked Out' when last room is checked out.

#### Room Management [/desk#room-management](/desk#room-management)
- Checked Out rooms will appear as Dirty
- select Dirty rooms and "Set as Clean" to bulk edit status

#### Shared
- Create a package "Sharing" and per Shared Bed add in pricing item.
- Room can be booked multiple times in in Booking when the "Shared" flag is selected.
- Use Extra Bed Count/Total Extra Bed Count to specifiy number of Beds for any Booking
- Each can be invoiced seperately

#### Dormitory
- Create a Room e.g. "Dormitory 102" and add beds numbered 1 to 14 or 18
- Use the Shared flag, select room no and set number beds in Extra Bed Count
- Select beds alloted in item level
- Create a room for each Dormitory room.
- Use Freshen Package if allotting for 'Freshen Up', rates as per package will be applied.. can select all beds
- Use mahatma/non mahatma package and select all beds to group dormitory booking.(same as individual, just select all beds) 

#### Payments
- Use "Make Payment" to make an advance before Invoice is generated. Payments section shows payments received in Booking.
- Select Cash/Cheque for mode of payment.
- Cheque no and cheque date fields are mandatory for cheque mode
- for Internal Customers (Departments) 'Make Payment' button is hidden. See process below for Internal Vouchers.

#### Invoice
- Use 'Make Invoice' to generate invoice
- After 'Make Invoice', invoice will be in 'Draft' status
- 'Submit' button should be displayed, Submit if no further changes required in invoice. For adding Services or applying Discount see next heading.
- Any advances received till then (i.e. payment made in the booking upto to this time) will be adjusted auto against invoice
- Payments made after Invoice is made, will be adjusted against invoice and invoice status will be updated to Paid if full outstanding is paid.
- If advance received was more than Invoice amount, then the difference will have to be refunded. 
- Make a payment for the refund amount and check the 'Refund' checkkbox. Click on the Payment line to refund.


#### Invoice Cancellation
- Cancel Sales Invoice
- If Advances have been adjusted against the invoice
- Open Journal Entry(s) (payments) made against Booking, which have been adjusted in Invoice Advances
- Cancel and amend Journal Entry and modify party lines
- Amend the Cancelled Invoice, make necessary changes and set advances. Submit Invoice.

#### Services
- Create services in Item Master (under Services) e.g. Breakage Charges, Laundry Service Charge etc,
- After 'Make Invoice', open invoice from link under 'Billing'
- Add selected service line in items, below rooms

#### Discount
- After 'Make Invoice', open invoice from link under 'Billing'
- Make necessary discount in Sales Invoice form and submit

#### Internal Vouchers 
- select Customer as respective department 
- Select "Instructed By". "Instructed By" - list of names to be added as contacts for Internal Departments
- "Make Payment" button is hidden for "Internal" customer group. Payment is settled on Approval.
- "Internal Voucher" report shows list of invoices against 'Internal' customer group. Filter by month/status 'Unpaid' to get list of Unpaid invoices for the month.
- Approve all selected invoices & send emails
- To amend, cancel the Sales Invoice and amend with desired items and amount. 
- Payment should be auto cancelled. Note: Rooms etc will not be affected, only billing part, so occupance etc remains same
- Auto email of IVs(Sales Invoice) can be done through backend, on configure date. 
- Report [Internal Voucher](/desk#query-report/Internal%20Voucher) All emails can be sent together or individually.
- If status is null, then email will be fired. After 7 days status will be changed to approved

#### Reports
- FrontDesk: Display routine booking details room wise. Will display room(s) based on current Room Status with Color Code
- Room Analytics: Room Type, Room & Item wise figures for management (same as created for suites)
- Occupancy: Display records as per booking status: CheckedIn, CheckedOut, Reserved, Billed, Bill To Be Raised (same as created for suites)
- Billing: Full Details of Sales Invoice with "Total Amount", "Paid", "Outstanding Amount", "Invoice Status" (same as created for suites)
- Hotel Trends: Will display room type wise as well as room wise occupancy statistics. (same as created for suites)
- Income Expense Summary - Will display total income and total expenses booked. This report will be submitted to A/c dept monthly (same as created in existing ASIM software)
