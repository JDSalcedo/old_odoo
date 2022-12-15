# -*- coding: utf-8 -*-
# Copyright 2017 Juan D. Salcedo Salazar, salcedo.salazar@gmail.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    cmp_type = fields.Selection([
        ('inv_fac', 'Factura'),
        ('inv_bol', 'Boleta'),
        ], string='Tipo de Comprobante')