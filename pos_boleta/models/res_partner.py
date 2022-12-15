# -*- coding: utf-8 -*-
# Copyright 2017 Juan D. Salcedo Salazar, salcedo.salazar@gmail.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, _

class Partner(models.Model):
    _inherit = 'res.partner'
    
    doc_number = fields.Char('Doc. Number', size=8)