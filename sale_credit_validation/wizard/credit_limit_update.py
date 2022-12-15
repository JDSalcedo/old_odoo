# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CreditLimitUpdate(models.TransientModel):
    _name = 'credit.limit.update'

    partner_id = fields.Many2one('res.partner', string='Client')
    name = fields.Monetary(string='Amount', currency_field='company_currency_id')
    start_date = fields.Datetime(string='Start date', default=fields.Datetime.now())
    finish_date = fields.Datetime(string='Finish date')
    valid = fields.Boolean(string='Valid', default=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user._get_company())
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)

    def update_partner_credit_limit(self):
        partner_cl_obj = self.env['res.partner.credit.limit']

        # Update partner credit limit
        self.partner_id.credit_limit = self.name

        # self._cr.execute("UPDATE %s SET valid=%s WHERE partner_id=%s "
        #                  % (partner_cl_obj._table, False, self.partner_id.id))

        partner_cl_obj.search([('partner_id', '=', self.partner_id.id)]).write({'valid': False})

        partner_cl_obj.create({
            'partner_id': self.partner_id.id,
            'name': self.name,
            'start_date': self.start_date,
            'finish_date': self.finish_date,
            'valid': self.valid,
            'company_id': self.company_id.id,
            'company_currency_id': self.company_currency_id.id,
            'user_id': self.user_id.id
        })
        return
