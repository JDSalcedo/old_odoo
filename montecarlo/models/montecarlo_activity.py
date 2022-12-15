# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class Activity(models.Model):
    _name='montecarlo.activity'
    
    name = fields.Char('Short Name')
    large_name = fields.Char('Large Name', required=True)
    start_day = fields.Date('Start Date')
    final_day = fields.Date('Finish Date')
    duration = fields.Integer('Duration(days)', compute='_compute_duration')
    start = fields.Boolean('Start', help="This activity is the root of the Sprint.", index=True)
    sprint_id = fields.Many2one('montecarlo.sprint', 'Sprint', required=True)
    probability_success = fields.Float('Probability Success(%)', default=100.0,
                                            help="Activity's percent of success",
                                            required=True)
    from_ids = fields.One2many('montecarlo.activity.transition', 'activity_to_id', string='Previous Activities')
    to_ids = fields.One2many('montecarlo.activity.transition', 'activity_from_id', string='Next Activities')
    earliest_start = fields.Integer('Earliest Start')
    earliest_finish = fields.Integer('Earliest Finish')
    lastest_start = fields.Integer('Lastest Start')
    lastest_finish = fields.Integer('Lastest Finish')
    
    def get_date_diff(self, date_ini, date_fin):
        sd = datetime.strptime(date_ini, DF)
        fd = datetime.strptime(date_fin, DF)
        return (fd - sd).days + 1
    
    @api.constrains('large_name')
    def _check_large_name(self):
        if len(self.large_name) == 1 and self.large_name == u's':
            raise ValidationError("The Name por de activity can not be the reserver letter 's'.")
    
    @api.constrains('probability_success')
    def _check_probability_success(self):
        if self.probability_success < 1 or self.probability_success > 100:
            raise ValidationError('Probability Distribution is a number between [1,100]')
    
    @api.one
    @api.depends('start_day', 'final_day')
    def _compute_duration(self):
        if self.final_day and self.start_day:
            self.duration = self.get_date_diff(self.start_day, self.final_day)
        else:
            self.duration = 0
            
    @api.onchange('start_day')
    def _onchange_start_day(self):
        warning = {}
        if self.start_day and self.final_day:
            if self.get_date_diff(self.start_day, self.final_day) <= 0:
                warning = {
                    'title': _("Warning for Start Date"),
                    'message': _("The Start Date should be equal to or less than Final Date.")
                    }
        res = {}
        if warning:
            res['warning'] = warning
            self.duration = 0
            self.start_day = False
        return res
        
    @api.onchange('final_day')
    def _onchange_final_day(self):
        warning = {}
        if self.start_day and self.final_day:
            if self.get_date_diff(self.start_day, self.final_day) <= 0:
                warning = {
                    'title': _("Warning for Final Date"),
                    'message': _("The Final Date should be equal to or greater than Start Date.")
                    }
        res = {}
        if warning:
            res['warning'] = warning
            self.duration = 0
            self.final_day = False
        return res
    
    @api.model
    def create(self, values):
        if values.has_key('large_name'):
            name = values['large_name'] if len(values['large_name']) < 50 else values['large_name'][:50]
            values['name'] = name
            if values.has_key('start_day') and values.has_key('final_day'):
                duration = self.get_date_diff(values['start_day'], values['final_day'])
                values['name'] = name + '(' + str(duration) + ')'
        return super(Activity, self).create(values)
            
    @api.multi
    def write(self, values):
        duration = 0
        lname = self.large_name
        if values.has_key('large_name'):
            lname = values['large_name']
        name = lname if len(lname) < 50 else lname[:50]
        values['name'] = name
        if values.has_key('start_day') and values.has_key('final_day'):
            duration = self.get_date_diff(values['start_day'], values['final_day'])
        elif values.has_key('start_day') and not values.has_key('final_day') and self.final_day:
            duration = self.get_date_diff(values['start_day'], self.final_day)
        elif values.has_key('final_day') and not values.has_key('start_day') and self.start_day:
            duration = self.get_date_diff(self.start_day, values['final_day'])
        elif not values.has_key('start_day') and not values.has_key('final_day') and self.start_day and self.final_day:
            duration = self.get_date_diff(self.start_day, self.final_day)
        
        values['name'] = name + '(' + str(duration) + ')'
        return super(Activity, self).write(values)
    
class ActivityTransition(models.Model):
    _name='montecarlo.activity.transition'
    
    name = fields.Char('Description')
    activity_from_id = fields.Many2one('montecarlo.activity', 'Previous Activity', required=True, ondelete="cascade")
    activity_to_id = fields.Many2one('montecarlo.activity', 'Next Activity', required=True, ondelete="cascade")
    
    @api.multi
    def _compute_name(self):
        for trans in self:
            if trans.activity_from_id:
                trans.name = 't = ' + str(trans.activity_from_id.duration)