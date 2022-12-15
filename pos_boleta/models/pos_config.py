# -*- coding: utf-8 -*-
# Copyright 2017 Juan D. Salcedo Salazar, salcedo.salazar@gmail.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _

class PosConfig(models.Model):
	_inherit = 'pos.config'
	
	@api.constrains('company_id', 'boleta_journal_id')
	def _check_company_journal(self):
		if self.boleta_journal_id and self.boleta_journal_id.company_id.id != self.company_id.id:
			raise UserError(_("The invoice journal and the point of sale must belong to the same company"))
	
	boleta_journal_id = fields.Many2one('account.journal', string='Boleta Journal', domain=[('type', '=', 'sale')],
		help="Accounting journal used to create Boletas.")
	final_journal_id = fields.Many2one('account.journal')
	local_printer_name = fields.Char('Nombre Impresora', help='Nombre de la impresora con la que esta registrada en el Sistema')
	local_server_ip = fields.Char('Server IP', help='IP de la computadora donde esta conectada la impresora, que es el mismo donde corre el PrintServer')
	local_server_port = fields.Char('Server Puerto', help='Puerto en el cual corre el servidor PrintServer')
	local_server_active = fields.Boolean('Activo', help='Indica si se usará el servidor local de impresión')