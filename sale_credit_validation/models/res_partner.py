# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # credit_limit = fields.Float(compute='_compute_current_credit_limit', store=True)
    spent_money = fields.Monetary(string='Spent Money', default=0.0)

    # @api.multi
    # def _compute_current_credit_limit(self):
    #     date = self._context.get('date') or fields.Date.today()
    #     company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
    #     # the subquery selects the last amount between 'start_date' and 'finish_date' for the given partner/company
    #     query = """SELECT rp.id, (SELECT cl.name FROM res_partner_credit_limit cl
    #                                   WHERE cl.partner_id = rp.id AND (cl.start_date <= %s AND %s <= cl.finish_date)
    #                                     AND (cl.company_id IS NULL OR cl.company_id = %s)
    #                                     AND cl.valid is true
    #                                ORDER BY cl.company_id, cl.start_date DESC
    #                                   LIMIT 1) AS amount
    #                    FROM res_partner rp
    #                    WHERE rp.id IN %s"""
    #     self._cr.execute(query, (date, date, company_id, tuple(self.ids)))
    #     credit_limits = dict(self._cr.fetchall())
    #     for partner in self:
    #         partner.credit_limit = credit_limits.get(partner.id) or 0.0

    def open_partner_credit_limit_history(self):
        """
        This function returns an action that display credit limits made for the given partners.
        """
        action = self.env.ref('sale_credit_validation.sale_credit_validation_action').read()[0]
        # action['domain'] = literal_eval(action['domain'])
        action['domain'] = [('partner_id', 'child_of', self.ids)]
        return action

    def open_partner_credit_limit_update(self):
        action = self.env.ref('sale_credit_validation.sale_credit_validation_action_update').read()[0]
        # action['domain'] = literal_eval(action['domain'])
        # action['domain'] = [('partner_id', 'child_of', self.ids)]
        return action


class PartnerCreditLimit(models.Model):
    _name = 'res.partner.credit.limit'
    _description = "Credit Limit"
    _order = "start_date desc, finish_date desc"

    partner_id = fields.Many2one('res.partner', string='Client')
    name = fields.Monetary(string='Amount', currency_field='company_currency_id')
    start_date = fields.Datetime(string='Start date')
    finish_date = fields.Datetime(string='Finish date')
    valid = fields.Boolean(string='Valid', default=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user._get_company())
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
