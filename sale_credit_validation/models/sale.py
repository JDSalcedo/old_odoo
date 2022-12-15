# -*- coding: utf-8 -*-

from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv.orm import setup_modifiers


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('charge_approval', 'Esperando Aprobación de Cobranzas'),
        ('manager_approval', 'Esperando Aprobación de Gerencia'),
        ('refuse', 'Rechazo')]
    )

    charge_manager_id = fields.Many2one(
        'res.users',
        string='Charge Manager',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    )
    account_manager_id = fields.Many2one(
        'res.users',
        string='Account Manager',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}

    )

    approve_charge_manager_id = fields.Many2one('res.users', string='Approve Charge Manager')
    approve_account_manager_id = fields.Many2one('res.users', string='Approve Account Manager')

    charge_manager_approve_date = fields.Datetime(string='Charge Manager Approval Date')
    account_manager_approve_date = fields.Datetime(string='Account Manager Approval Date')

    refuse_user_id = fields.Many2one('res.users', string="Refused By")
    refuse_date = fields.Date(string="Refused Date")
    refuse_reason_note = fields.Text(string="Refuse Reason")

    credit_limit_validation = fields.Boolean(
        compute='_compute_credit_limit_validation'
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.env.user.has_group('product.group_sale_pricelist') and doc.xpath("//field[@name='pricelist_id']"):
            node = doc.xpath("//field[@name='pricelist_id']")[0]
            if self.env.user.has_group('sales_team.group_sale_manager'):
                node.set('readonly', '0')
            elif self.env.user.has_group('sales_team.group_sale_salesman') or \
                    self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
                node.set('readonly', '1')
            setup_modifiers(node, res['fields']['pricelist_id'])
        res['arch'] = etree.tostring(doc)
        return res

    @api.depends('company_id')
    def _compute_credit_limit_validation(self):
        # self.credit_limit_validation = self.env['ir.values'].get_default(
        #                                                         'sale.config.settings',
        #                                                         'credit_limit_validation_setting'
        #                                                     )
        self.credit_limit_validation = self.env.user.company_id.credit_limit_validation

    def get_partner_credit_limit(self, partner_id):
        date = self._context.get('date') or fields.Datetime.now()
        company_id = self._context.get('company_id') or self.env.user.company_id.id
        # the subquery selects the last amount between 'start_date' and 'finish_date' for the given partner/company
        query = """SELECT rp.id, (SELECT cl.name FROM res_partner_credit_limit cl
                                      WHERE cl.partner_id = rp.id AND (cl.start_date <= %s AND %s <= cl.finish_date)
                                        AND (cl.company_id IS NULL OR cl.company_id = %s)
                                        AND cl.valid is true
                                   ORDER BY cl.company_id, cl.start_date DESC
                                      LIMIT 1) AS amount
                       FROM res_partner rp
                       WHERE rp.id = %s"""
        self._cr.execute(query, (date, date, company_id, partner_id))
        credit_limits = dict(self._cr.fetchall())
        return credit_limits.get(partner_id) or 0.0

    @api.multi
    def action_confirm(self):
        if self._context.get('call_super', False):
            return super(SaleOrder, self).action_confirm()

        if self.env.user.company_id.credit_limit_validation:
            for sale in self:
                credit_limit = self.env.user.company_id.currency_id.compute(
                    self.get_partner_credit_limit(sale.partner_id.id), self.env.user.company_id.currency_id)
                spent_money = self.env.user.company_id.currency_id.compute(
                    sale.partner_id.spent_money, self.env.user.company_id.currency_id)
                balance = credit_limit - spent_money

                if balance <= 0.0:
                    raise UserError(_('Credit limit expired or 0.00 for the Client "%s".')
                                    % sale.partner_id.display_name)
                amount_total = sale.currency_id.compute(
                    sale.amount_total, sale.company_id.currency_id)
                if amount_total > balance and sale.state != 'charge_approval':
                    if not sale.charge_manager_id:
                        raise UserError(_('Please select Charge Manager.'))
                    email_to = sale.charge_manager_id.email
                    email_template_id = self.env.user.company_id.email_template_id
                    ctx = self._context.copy()
                    ctx.update({'name': sale.charge_manager_id.name})

                    if email_template_id:
                        email_template_id.with_context(ctx).send_mail(
                            self.id,
                            email_values={
                                'email_to': email_to,
                                'subject': _('Sale Order: ') + sale.name + _(' (Approval Waiting)')}
                        )
                    sale.write({'state': 'charge_approval'})
                else:
                    sale.partner_id.spent_money = sale.partner_id.spent_money + amount_total
                    return super(SaleOrder, self).action_confirm()
        else:
            return super(SaleOrder, self).action_confirm()

        return True

    @api.multi
    def button_charge_approval(self):
        for sale in self:
            if not sale.account_manager_id:
                raise UserError(_('Please select Account Manager.'))
            else:
                email_to = sale.charge_manager_id.email
                email_template_id = self.env.user.company_id.email_template_id
                ctx = self._context.copy()
                ctx.update({'name': sale.charge_manager_id.name})

                if email_template_id:
                    email_template_id.with_context(ctx).send_mail(
                        self.id,
                        email_values={
                            'email_to': email_to,
                            'subject': _('Sale Order: ') + sale.name + _(' (Approval Waiting)')}
                    )
                sale.write({
                    'state': 'manager_approval',
                    'approve_charge_manager_id': self.env.user.id,
                    'charge_manager_approve_date': fields.Datetime.now(),
                })

    @api.multi
    def button_manager_approval(self):
        for sale in self:
            sale.partner_id.spent_money = sale.partner_id.credit_limit
            sale.write({
                'approve_account_manager_id': self.env.user.id,
                'account_manager_approve_date': fields.Datetime.now(),
            })
            sale.with_context(call_super=True).action_confirm()
        return True
