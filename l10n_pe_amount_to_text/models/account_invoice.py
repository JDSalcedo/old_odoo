# -*- coding: utf-8 -*-

import amount_to_text_es_PE

from odoo import api, fields, models, _

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.one
    @api.depends('amount_total')
    def _get_amount_to_text(self):
        amount_to_text = amount_to_text_es_PE.get_amount_to_text(
            self, self.amount_total, 'es_cheque', self.currency_id.name)
        self.amount_to_text = amount_to_text + (self.currency_id.name_large and self.currency_id.name_large.upper() or '')
    
    amount_to_text = fields.Char(string='Son', size=256, compute='_get_amount_to_text')