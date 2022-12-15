# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import date


class StudentFile(models.Model):
    _name = 'student.file'
    _inherits = {'res.partner': 'partner_id'}
    _order = 'name'

    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True,
                                 string='Related Partner')
    surname = fields.Char('Surname')
    dni = fields.Char('DNI', size=8,
                      help="DNI is a number of size 8")
    age = fields.Integer('Age', compute='_compute_age_from_birthdate', store=True)
    birthdate = fields.Date('Birthdate')
    brothers = fields.Integer('# Brothers')
    father = fields.Char('Father')
    fathers_birthdate = fields.Date("Father's Birthdate")
    fathers_age = fields.Char("Father's Age", compute='_compute_age_from_fathers_birthdate', store=True)
    fathers_occupation = fields.Char("Father's Occupation")
    fathers_mobile = fields.Char("Father's Mobile", size=9)
    mother = fields.Char('Mother')
    mothers_birthdate = fields.Date("Mother's Birthdate")
    mothers_age = fields.Char("Mother's Age", compute='_compute_age_from_mothers_birthdate', store=True)
    mothers_occupation = fields.Char("Mother's Occupation")
    mothers_mobile = fields.Char("Mother's Mobile", size=9)
    lives_with_type = fields.Selection(
        [('both', 'Both parents'),
         ('father', 'Father'),
         ('mother', 'Mother'),
         ('other', 'Other family')], string='Lives With')
    reason = fields.Text('Reason')
    beggin = fields.Integer('Year of Begginning in the Institution')
    status = fields.Selection(
        [('new', 'New'),
         ('continuous', 'Continuous'),
         ('reentry', 'Re-entry')], string='Status')
    repeating = fields.Selection(
        [('yes', 'Yes'),
         ('no', 'No')], string='Repeating')

    incidences_ids = fields.One2many('incidence.file', 'student_id', string='Incidences')
    count_incidences = fields.Integer('Incidences #', compute='_compute_count_incidences', store=True)

    @api.onchange('lives_with_type')
    def _onchange_lives_with_type(self):
        if self.lives_with_type != 'other':
            self.reason = False
        return

    def calculate_age(self, born):
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @api.constrains('dni')
    def _check_dni(self):
        if len(self.dni) == 8:
            try:
                int(self.dni)
            except:
                raise ValidationError(_("DNI should have just numbers."))
        else:
            raise ValidationError(_("DNI should have 8 characters."))

    @api.constrains('fathers_mobile')
    def _check_fathers_mobile(self):
        if self.fathers_mobile:
            if len(self.fathers_mobile) == 9:
                try:
                    int(self.fathers_mobile)
                except:
                    raise ValidationError(_("Father's Mobile should have just numbers."))
            else:
                raise ValidationError(_("Father's Mobile should have 9 characters."))

    @api.constrains('mothers_mobile')
    def _check_mothers_mobile(self):
        if self.mothers_mobile:
            if len(self.mothers_mobile) == 9:
                try:
                    int(self.mothers_mobile)
                except:
                    raise ValidationError(_("Mother's Mobile should have just numbers."))
            else:
                raise ValidationError(_("Mother's Mobile should have 9 characters."))

    @api.one
    @api.depends('birthdate')
    def _compute_age_from_birthdate(self):
        if self.birthdate:
            year, month, day = map(int, self.birthdate.split("-"))
            birthdate = date(year, month, day)
            self.age = self.calculate_age(birthdate)

    @api.one
    @api.depends('fathers_birthdate')
    def _compute_age_from_fathers_birthdate(self):
        if self.fathers_birthdate:
            year, month, day = map(int, self.fathers_birthdate.split("-"))
            birthdate = date(year, month, day)
            self.fathers_age = self.calculate_age(birthdate)

    @api.one
    @api.depends('mothers_birthdate')
    def _compute_age_from_mothers_birthdate(self):
        if self.mothers_birthdate:
            year, month, day = map(int, self.mothers_birthdate.split("-"))
            birthdate = date(year, month, day)
            self.mothers_age = self.calculate_age(birthdate)

    @api.multi
    @api.depends('name', 'surname')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.surname:
                name = "%s - %s %s" % (record.dni, name, record.surname)
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), '|', ('surname', operator, name), ('dni', operator, name)]
        pos = self.search(domain + args, limit=limit)
        return pos.name_get()

    @api.one
    @api.depends('incidences_ids')
    def _compute_count_incidences(self):
        if self.incidences_ids:
            self.count_incidences = len(self.incidences_ids.ids)
        else:
            self.count_incidences = 0

    @api.multi
    def show_incidences(self):
        self.ensure_one()

        incidences = self.mapped('incidences_ids')
        view_mode = 'tree,form,pivot'
        view_tree_id = self.env.ref('student_file.view_incidence_file_tree').id
        view_form_id = self.env.ref('student_file.view_incidence_file_form').id
        view_pivot_id = self.env.ref('student_file.view_incidence_file_pivot').id

        res_id = False
        domain = [('student_id', '=', self.id)]
        context = {'default_student_id': self.id}
        if len(incidences) >= 1:
            domain = [('id', 'in', incidences.ids), ('student_id', '=', self.id)]

        return {
            'name': (_("Incidences")),
            'type': 'ir.actions.act_window',
            'view_mode': view_mode,
            'res_model': 'incidence.file',
            'target': 'self',
            'views': [(view_tree_id, 'tree'),
                      (view_form_id, 'form'),
                      (view_pivot_id, 'pivot')],
            'view_id': view_tree_id,
            'res_id': res_id,
            'domain': domain,
            'context': context,
        }

    @api.multi
    def write(self, vals):
        if vals.has_key('lives_with_type') and vals.get('lives_with_type') != 'other':
            vals['reason'] = False
        return super(StudentFile, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.has_key('lives_with_type') and vals.get('lives_with_type') != 'other':
            vals['reason'] = False
        return super(StudentFile, self).create(vals)