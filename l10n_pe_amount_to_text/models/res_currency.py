# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Currency(models.Model):
    _inherit = 'res.currency'
    
    name_large = fields.Char('Nombre Largo')