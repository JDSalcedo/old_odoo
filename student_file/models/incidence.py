# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class IncidenceFile(models.Model):
    _name = 'incidence.file'
    
    name = fields.Char(string='Incidence Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    student_id = fields.Many2one('student.file', string='Student')
    image = fields.Binary("Image", related='student_id.image', attachment=True)
    image_medium = fields.Binary("Medium-sized image", related='student_id.image_medium', attachment=True)
    image_small = fields.Binary("Small-sized image", related='student_id.image_small', attachment=True)
    date = fields.Date('Date', copy=False)
    derived_by = fields.Selection(
        [('teacher', 'Teacher'),
         ('assistant', 'Assistant'),
         ('coordinator', 'Coordinator'),
         ('director', 'Director'),
         ('psycho', 'Psychology')], string='Derived by')
    reason_type = fields.Selection(
        [('learning', 'Learning'),
         ('behavior', 'Behavior'),
         ('family', 'Family'),
         ('personal_inter', 'Personal interview'),
         ('parents_inter', 'Parents interview'),
         ('other', 'Others')], string='Reason')
    description = fields.Text('Description')
    counseling = fields.Text('Counseling')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('incidence.file') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('incidence.file') or _('New')
        return super(IncidenceFile, self).create(vals)
