# -*- coding: utf-8 -*-
# Copyright 2017 Juan D. Salcedo Salazar, salcedo.salazar@gmail.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import amount_to_text_es_PE

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'
	
	def blank_matrix(self):
		return [[" " for j in range(137)] for i in range(36)]
	
	def isfloat(self, value):
		"""
			Funcion que permite determinar si una cadena puede ser convertida en float,
			esta funcion es usada para determinar si la candena esta compuesta solo por numeros.
		"""
		try:
			float(value)
			return True
		except ValueError:
			return False
	
	def reemplazar(self, posx, posy, max, cad, matrix):
		"""
			Esta funcion nos permite llenar la matrix con una cadena 'cad', 
			en una determinada posicion 'posx', 'posy', 
			tambien permite indicarle el numero maximo de caracteres permitidos.
		"""
		i = posx
		if self.isfloat(cad):
			cad = str(cad)
		if len(cad) > max:
			cad = cad[:max]
		for letter in cad:
			matrix[posy][i] = letter
			i+=1
		return matrix
	
	def reemplazar_ultimo(self, posx, posy, max, cad, matrix):
		""""
			Esta funcion nos permite llenar la matrix con una cadena 'cad', 
			en una determinada posicion 'posx', 'posy', 
			tambien permite indicarle el numero maximo de caracteres permitidos. 
			La unica diferencia es que coloca la cadena desde el final de la cadena hasta al inicio.
		"""
		i = posx
		if self.isfloat(cad):
			cad = str(cad)
		if len(cad) > max:
			cad = cad[:max]
		cad = cad[::-1]
		for letter in cad:
			matrix[posy][i] = letter
			i-=1
		return matrix
	
	def _get_matrix_string(self, matrix):
		cad = ""
		for i in range(0,36):
			for j in range(0,137):
				try:
					cad += matrix[i][j]
				except ValueError:
					cad += '?'
			cad+="\n"
		return cad
	
	def comp_factura(self, matrix, igv_inc=True):
		"""
			Función que recibe como parametro una matriz que solo contiene espacios en blanco,
			y dependiendo del campo va colocando datos en las diferentes posiciones indicadas
			para la factura
		"""
		#Doc. Origen
		if self.origin:
			matrix = self.reemplazar(22, 7, 12, self.origin, matrix)
		#Numero de comprobante
		if self.number:
			matrix = self.reemplazar(122, 7, 11, self.number, matrix)
		if self.partner_id:
			#Cliente
			matrix = self.reemplazar(22, 9, 110, self.partner_id.name, matrix)
			#Colocando la direccion
			if self.partner_id.street:
				matrix = self.reemplazar(22, 10, 110, self.partner_id.street, matrix)
			#Número de documento
			matrix = self.reemplazar(122, 10, 11, self.partner_id.doc_number, matrix)
		if self.date_invoice:
			fecha = self.date_invoice[8:10]+'/'+self.date_invoice[5:7]+'/'+self.date_invoice[0:4]
			matrix = self.reemplazar(122, 9 ,10, fecha, matrix)
		#líneas de comprobante
		linea = 15
		for line in self.invoice_line_ids:
			#cantidad
			matrix = self.reemplazar(12, linea, 7, line.quantity, matrix)
			#unid/med
			matrix = self.reemplazar(22, linea, 7, line.product_id.product_tmpl_id.uom_po_id.name, matrix)
			#descripcion
			matrix = self.reemplazar(30, linea, 53, line.product_id.name, matrix)
			#precio unitario = total / cantidad
			pu = igv_inc and line.price_unit or ((line.price_unit * 100) / (100 + 18))
			matrix = self.reemplazar_ultimo(120, linea, 11, "{0:,.2f}".format(pu), matrix)
			#valor total
			psubt = igv_inc and (line.price_unit * line.quantity) or \
				(((line.price_unit * 100) / (100 + 18)) * line.quantity)
			matrix = self.reemplazar_ultimo(136, linea, 14, "{0:,.2f}".format(psubt), matrix)
			linea+=1
		
		#El monto en texto
		matrix = self.reemplazar( 17, 29, 90, self.amount_to_text, matrix)
		#Pago
		matrix = self.reemplazar_ultimo(136, 29, 14, self.payment_term_id.name, matrix)
		#Si es Factura('inv_fac')
		if self.cmp_type == 'inv_fac':
			#SubTotal
			self.reemplazar(30, 30, 14, "{0:,.2f}".format(self.amount_untaxed), matrix)
			#Impuesto
			self.reemplazar(70, 30, 14, "{0:,.2f}".format(self.amount_tax), matrix)
		#Total
		matrix = self.reemplazar_ultimo(136, 30, 14, "{0:,.2f}".format(self.amount_total), matrix)

		return self._get_matrix_string(matrix)
	
	@api.model
	def pos_matrix_print(self, inv_id, igv_inc=True):
		PosOrder = self.env['pos.order']
		matrix = self.blank_matrix()
		selected_order = PosOrder.browse([inv_id])
		inv_obj = selected_order.invoice_id
		return inv_obj.comp_factura(matrix, igv_inc)
	
	@api.one
	def _compute_matrix_print(self):
		matrix = self.blank_matrix()
		_logger.info(self.comp_factura(matrix))
		_logger.info(self.comp_factura(matrix, False))
		self.impresion = self.comp_factura(matrix)

	@api.multi
	def invoice_pre_print(self):
		""" Print the invoice and mark it as sent, so that we can see more
			easily the next step of the workflow
		"""
		self.ensure_one()
		self.sent = True
		return self.env['report'].get_action(self, 'pos_boleta.report_pre_invoice')
	
	matrix_print = fields.Text('', compute="_compute_matrix_print")
	cmp_type =fields.Selection([
        ('inv_fac', 'Factura'),
        ('inv_bol', 'Boleta'),
        ], string='Tipo de Comprobante', related='journal_id.cmp_type') 