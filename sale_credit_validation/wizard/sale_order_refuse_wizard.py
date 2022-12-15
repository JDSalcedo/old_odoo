# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SaleOrderRefuseWizard(models.TransientModel):
    _name = 'sale.order.refuse.wizard'

    note = fields.Text(
        string="Refuse Reason",
        required=True,
    )

    @api.multi
    def action_so_refuse(self):
        sale_order_id = self.env['sale.order'].browse(int(self._context.get('active_id')))
        for rec in self:
            sale_order_id.refuse_reason_note = rec.note
            sale_order_id.refuse_user_id = rec.env.uid
            sale_order_id.refuse_date = fields.Datetime.now()
            refuse_template_id = rec.env.user.company_id.refuse_template_id
#             mail = self.env['mail.template'].browse(refuse_template_id)
            ctx = self._context.copy()

            if sale_order_id.state == 'charge_approval':
                ctx.update({
                    'name': sale_order_id.create_uid.partner_id.name,
                    'email_to': sale_order_id.create_uid.partner_id.email,
                    'subject': _('Sale Order: ') + sale_order_id.name + _(' Refused'),
                    'manager_name': _('Charge Manager: ') + self.env.user.partner_id.name,
                    'reason': rec.note,
                    })
            if sale_order_id.state == 'manager_approval':
                ctx.update({
                    'name': sale_order_id.create_uid.partner_id.name,
                    'email_to': sale_order_id.create_uid.partner_id.email,
                    'subject': _('Sale Order: ') + sale_order_id.name + _(' Refused'),
                    'manager_name': _('Account Manager: ') + self.env.user.partner_id.name,
                    'reason': rec.note,
                    })
            if refuse_template_id and sale_order_id.state in ['charge_approval', 'manager_approval']:
                refuse_template_id.with_context(ctx).send_mail(sale_order_id.id)
            sale_order_id.state = 'refuse'
