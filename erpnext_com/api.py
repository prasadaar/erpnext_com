from __future__ import unicode_literals
import frappe
from frappe import _
from central.signup import signup as _signup

from razorpay_integration.api import get_razorpay_checkout_url

# TODO:
# 1. send email to particpant and us
# 2. who is coming page
# 3. final design

@frappe.whitelist(allow_guest=True)
def make_payment(full_name, email, company, workshop=0, conference=0):
	amount = int(workshop or 0) * 2000 + int(conference or 0) * 600

	if not amount:
		frappe.msgprint('Please set no of tickets')
		return

	participant = frappe.get_doc({
		'doctype': 'Conference Participant',
		'full_name': full_name,
		'email_id': email,
		'company_name': company,
		'workshop': workshop,
		'conference': conference,
		'amount': amount
	}).insert(ignore_permissions=True)

	url = get_razorpay_checkout_url(**{
		'amount': amount,
		'title': 'ERPNext Conference Tickets',
		'description': '{0} passes for conference, {1} passes for workshop'.format(int(conference or 0), int(workshop or 0)),
		'payer_name': full_name,
		'payer_email': email,
		'doctype': participant.doctype,
		'name': participant.name,
		'order_id': participant.name
	})

	return url

@frappe.whitelist(allow_guest=True)
def signup(full_name, email, subdomain, plan="Free", distribution="erpnext"):
	status = _signup(full_name, email, subdomain, plan=plan, distribution='erpnext' if distribution=='schools' else distribution)

	context = {
		'pathname': 'schools/signup' if distribution=='schools' else 'signup'
	}

	if status == 'success':
		location = frappe.redirect_to_message(_('Thank you for signing up'),
			"""<div><p>You will receive an email at <strong>{}</strong>,
			asking you to verify this account request.<br>
			If you are unable to find the email in your inbox, please check your SPAM folder.
			It may take a few minutes before you receive this email.</p>
			<p>Once you click on the verification link, your account will be ready in a few minutes.</p>
			</div>""".format(email), context=context)

	elif status=='retry':
		return {}

	else:
		# something went wrong
		location = frappe.redirect_to_message(_('Something went wrong'),
			'Please try again or drop an email to support@erpnext.com',
			context=context)

	return {
		'location': location
	}
