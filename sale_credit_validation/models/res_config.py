# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    credit_limit_validation_setting = fields.Boolean(
        related='company_id.credit_limit_validation',
        string='Credit Limit Validation'
    )

    # @api.multi
    # def set_credit_limit_validation_defaults(self):
    #     return self.env['ir.values'].sudo().set_default(
    #         'sale.config.settings', 'credit_limit_validation_setting', self.credit_limit_validation_setting)
