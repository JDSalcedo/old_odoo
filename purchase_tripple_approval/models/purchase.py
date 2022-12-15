# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('state')
    def _set_purchase_user(self):
        for rec in self:
            if rec.state == 'draft' or 'sent':
                rec.purchase_user_id = self.env.user.id,

    @api.model
    def _get_assembly_validation_amount(self):
#         assembly_validation_amount = self.env['ir.values'].get_default('purchase.config.settings', 'assembly_validation_amount')
        assembly_validation_amount = self.env.user.company_id.assembly_validation_amount
        return assembly_validation_amount

    @api.model
    def _get_director_validation_amount(self):
#         director_validation_amount = self.env['ir.values'].get_default('purchase.config.settings', 'director_validation_amount')
        director_validation_amount = self.env.user.company_id.director_validation_amount
        return director_validation_amount

    @api.model
    def _get_three_step_validation(self):
#         three_step_validation = self.env['ir.values'].get_default('purchase.config.settings', 'three_step_validation')
        three_step_validation = self.env.user.company_id.three_step_validation
        return three_step_validation

    @api.model
    def _get_email_template_id(self):
#         email_template_id = self.env['ir.values'].get_default('purchase.config.settings', 'email_template_id')
        email_template_id = self.env.user.company_id.email_template_id
        return email_template_id

    @api.model
    def _get_refuse_template_id(self):
#         refuse_template_id = self.env['ir.values'].get_default('purchase.config.settings', 'refuse_template_id')
        refuse_template_id = self.env.user.company_id.refuse_template_id
        return refuse_template_id

    state = fields.Selection(selection_add=[
        ('department_approval', 'Esperando Aprobación de Compras'),
        ('assembly_approval', 'Esperando Aprobación de Gerencia'),
        ('director_approval', 'Esperando Aprobación de Directorio'),
        ('refuse', 'Refuse')],
        string='Status',
    )
    po_refuse_user_id = fields.Many2one(
        'res.users',
        string="Refused By",
        readonly = True,
    )
    po_refuse_date = fields.Date(
        string="Refused Date",
        readonly=True
    )
    refuse_reason_note = fields.Text(
        string="Refuse Reason",
        readonly=True
    )
    dept_manager_id = fields.Many2one(
        'res.users',
        string='Purchase/Department Manager',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}
    )
    assembly_manager_id = fields.Many2one(
        'res.users',
        string='Assembly Manager',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}
    )
    director_manager_id = fields.Many2one(
        'res.users',
        string='Director Manager',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}
    )
    approve_dept_manager_id = fields.Many2one(
        'res.users',
        string='Approve Department Manager',
        readonly=True,
    )
    approve_assembly_manager_id = fields.Many2one(
        'res.users',
        string='Approve Assembly Manager',
        readonly=True,
    )
    approve_director_manager_id = fields.Many2one(
        'res.users',
        string='Approve Director Manager',
        readonly=True,
    )
    dept_manager_approve_date = fields.Datetime(
        string='Department Manager Approve Date',
        readonly=True,
    )
    assembly_manager_approve_date = fields.Datetime(
        string='Assembly Manager Approve Date',
        readonly=True,
    )
    director_manager_approve_date = fields.Datetime(
        string='Director Manager Approve Date',
        readonly=True,
    )
    purchase_user_id = fields.Many2one(
        'res.users',
        string='Purchase User',
        compute='_set_purchase_user',
        store=True,
    )


    @api.multi
    def _write(self, vals):
        for order in self:
            amount_total = order.currency_id.compute(order.amount_total, order.company_id.currency_id)
            assembly_validation_amount = self._get_assembly_validation_amount()
            po_double_validation_amount = self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id)
            if vals.get('state') == 'department_approval':
                if not order.dept_manager_id:
                    raise UserError(_('Please select Purchase/Department Manager.'))
                else:
                    email_to = order.dept_manager_id.email
                    email_template_id = self._get_email_template_id()
                    ctx = self._context.copy()
                    ctx.update({'name': order.dept_manager_id.name})
                    #reminder_mail_template.with_context(ctx).send_mail(user)
                    if email_template_id:
                        email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + order.name + _(' (Approval Waiting)')})

            if vals.get('state') == 'assembly_approval':
                if not order.assembly_manager_id:
                    raise UserError(_('Please select Assembly Manager.'))
                else:
                    email_to = order.assembly_manager_id.email
                    email_template_id = self._get_email_template_id()
#                     mail = self.env['mail.template'].browse(email_template_id)
                    ctx = self._context.copy()
                    ctx.update({'name': order.assembly_manager_id.name})
                    #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Assembly Manager Approve"})
                    if email_template_id:
                        email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + order.name + _(' (Approval Waiting)')})

            if vals.get('state') == 'director_approval':
                if not order.director_manager_id:
                    raise UserError(_('Please select Director Manager.'))
                else:
                    email_to = order.director_manager_id.email
                    email_template_id = self._get_email_template_id()
#                     mail = self.env['mail.template'].browse(email_template_id)
                    ctx = self._context.copy()
                    ctx.update({'name': order.director_manager_id.name})
                    #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Director Manager Approve"})
                    if email_template_id:
                        email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + order.name + _(' (Approval Waiting)')})

            if order.state == 'department_approval' and vals.get('state') == 'purchase':
                order.approve_dept_manager_id = self.env.user.id
                order.dept_manager_approve_date = fields.Datetime.now()
            elif order.state == 'department_approval' and vals.get('state') == 'assembly_approval':
                order.approve_dept_manager_id = self.env.user.id
                order.dept_manager_approve_date = fields.Datetime.now()

            if order.state == 'assembly_approval' and vals.get('state') == 'purchase':
                order.approve_assembly_manager_id = self.env.user.id
                order.assembly_manager_approve_date = fields.Datetime.now()
            elif order.state == 'assembly_approval' and vals.get('state') == 'director_approval':
                order.approve_assembly_manager_id = self.env.user.id
                order.assembly_manager_approve_date = fields.Datetime.now()

            if order.state == 'director_approval' and vals.get('state') == 'purchase':
                order.approve_director_manager_id = self.env.user.id
                order.director_manager_approve_date = fields.Datetime.now()
        return super(PurchaseOrder, self)._write(vals)


    @api.multi
    def button_assembly_approval(self):
        director_validation_amount = self._get_director_validation_amount()
        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
        for order in self:
            if amount_total > director_validation_amount:
                order.write({'state': 'director_approval'})
            if amount_total < director_validation_amount:
                order.button_director_approval()
        return True

    @api.multi
    def button_director_approval(self):
        for order in self:
            order.with_context(call_super=True).button_approve()
        return True
    
    @api.multi
    def button_department_approval(self):
        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
        assembly_validation_amount = self._get_assembly_validation_amount()
        
        for order in self:
            if amount_total < assembly_validation_amount:
                return order.button_director_approval()
            if amount_total > assembly_validation_amount:
                order.write({'state': 'assembly_approval'})
        return True

    @api.multi
    def button_approve(self, force=False):
        if self._context.get('call_super', False):
            return super(PurchaseOrder, self).button_approve()

        three_step_validation = self._get_three_step_validation()
        if not three_step_validation:
            return super(PurchaseOrder, self).button_approve() 

        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
        po_double_validation_amount = self.env.user.company_id.currency_id.compute(self.company_id.po_double_validation_amount, self.currency_id)

        if three_step_validation and not self._context.get('call_super', False):
            for order in self:
                if order.user_has_groups('purchase.group_purchase_manager'):
                    if amount_total > po_double_validation_amount and order.state != 'department_approval':
                        order.write({'state': 'department_approval'})
                    elif order.state == 'department_approval':
                        order.state = 'assembly_approval'
                    else:
                        return super(PurchaseOrder, self).button_approve()
                else:
                    order.write({'state': 'to approve'})

        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
