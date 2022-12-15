# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    credit_limit_validation = fields.Boolean("Credit Limit Validation")

    email_template_id = fields.Many2one(
        'mail.template',
        string='Sale Approval Email Template',
    )
    refuse_template_id = fields.Many2one(
        'mail.template',
        string='Sale Refuse Email Template',
    )
