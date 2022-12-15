# -*- coding: utf-8 -*-
# Copyright 2017 Juan D. Salcedo Salazar, salcedo.salazar@gmail.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, tools, _

class PosOrder(models.Model):
	_inherit = 'pos.order'
	
	def _prepare_invoice(self):
		"""
			Se sobreescribe esta funcion encargada de crear los valores del
			registro account_invoice, y actualizamos 'journal_id' asignandole
			nuestra variable('final_journal_id') que corresponde al diario 
			seleccionado desde el POS.
		"""
		res = super(PosOrder, self)._prepare_invoice()
		if self.session_id.config_id.final_journal_id and self.session_id.config_id.final_journal_id.id:
			res.update({'journal_id': self.session_id.config_id.final_journal_id.id})
		return res

	@api.model
	def _process_order(self, pos_order):
		"""
			Se le asigna a la session el diario final, para luego ser usado
			al momento de facturar
		"""
		order = super(PosOrder, self)._process_order(pos_order)
		if pos_order.has_key('final_journal_id'):
			order.session_id.config_id.final_journal_id = pos_order['final_journal_id']
		return order