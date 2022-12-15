# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class Process(models.Model):
    _name='montecarlo.process'
    
    name = fields.Char('Short Name')
    large_name = fields.Char('Large Name', required=True)
    start_day = fields.Date('Start Date')
    final_day = fields.Date('Finish Date')
    duration = fields.Integer('Duration(days)', compute='_compute_duration')
    start = fields.Boolean('Start', help="This Process is the root of the Project.", index=True)
    project_id = fields.Many2one('montecarlo.project', 'Project', required=True)
    probability_success = fields.Float('Probability Success(%)', default=100.0,
                                            help="Process' percent of success",
                                            required=True)
    from_ids = fields.One2many('montecarlo.process.transition', 'process_to_id', string='Previous Processes')
    to_ids = fields.One2many('montecarlo.process.transition', 'process_from_id', string='Next Processes')
    earliest_start = fields.Integer('Earliest Start')
    earliest_finish = fields.Integer('Earliest Finish')
    lastest_start = fields.Integer('Lastest Start')
    lastest_finish = fields.Integer('Lastest Finish')
    slack = fields.Integer('Slack')
    
    def get_date_diff(self, date_ini, date_fin):
        sd = datetime.strptime(date_ini, DF)
        fd = datetime.strptime(date_fin, DF)
        return (fd - sd).days + 1
    
    @api.constrains('large_name')
    def _check_large_name(self):
        if len(self.large_name) == 1 and self.large_name == u's':
            raise ValidationError("The Name por de process can not be the reserver letter 's'.")
    
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
    
    @api.model
    def create(self, values):
        if values.has_key('large_name'):
            name = values['large_name'] if len(values['large_name']) < 50 else values['large_name'][:50]
            values['name'] = name
            if values.has_key('start_day') and values.has_key('final_day'):
                duration = self.get_date_diff(values['start_day'], values['final_day'])
                values['name'] = name + '(' + str(duration) + ')'
        
        if values.has_key('start_day') and values.has_key('final_day'):
            duration = self.get_date_diff(values['start_day'], values['final_day'])
            if self.get_date_diff(values['start_day'], values['final_day']) <= 0:
                raise ValidationError(_('The Start Date should be equal to or less than Final Date.'))
            else:
                project = self.env['montecarlo.project'].search([('id', '=', values['project_id'])])
                if self.get_date_diff(project.start_day, values['start_day']) <= 0:
                    raise ValidationError(_("The Start Date should be equal to or greater than Project's Start Date."))
                if self.get_date_diff(values['final_day'], project.final_day) <= 0:
                    raise ValidationError(_("The Final Date should be equal to or less than Project's Final Date."))
        
        return super(Process, self).create(values)
            
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
            if self.get_date_diff(values['start_day'], values['final_day']) <= 0:
                raise ValidationError(_('The Start Date should be equal to or less than Final Date.'))
            else:
                if self.get_date_diff(self.project_id.start_day, values['start_day']) <= 0:
                    raise ValidationError(_("The Start Date should be equal to or greater than Project's Start Date."))
                if self.get_date_diff(values['final_day'], self.project_id.final_day) <= 0:
                    raise ValidationError(_("The Final Date should be equal to or less than Project's Final Date."))
                
                for from_id in self.from_ids:
                    if from_id.process_from_id.final_day:
                        if self.get_date_diff(from_id.process_from_id.final_day, values['start_day']) <= 0:
                            raise ValidationError(_("The Start Date should be equal to or greater than the Final Date of '%s' process" %(from_id.process_from_id.large_name)))
                            break
                    else:
                        raise ValidationError(_("You should complete the dates for the previous process '%s'" %(from_id.process_from_id.large_name)))
                        break
        elif values.has_key('start_day') and not values.has_key('final_day') and self.final_day:
            duration = self.get_date_diff(values['start_day'], self.final_day)
            if self.get_date_diff(values['start_day'], self.final_day) <= 0:
                raise ValidationError(_('The Start Date should be equal to or less than Final Date.'))
            else:
                for from_id in self.from_ids:
                    if from_id.process_from_id.final_day:
                        if self.get_date_diff(from_id.process_from_id.final_day, values['start_day']) <= 0:
                            raise ValidationError(_("The Start Date should be equal to or greater than the Final Date of '%s' process" %(from_id.process_from_id.large_name)))
                            break
                    else:
                        raise ValidationError(_("You should complete the dates for the previous process '%s'" %(from_id.process_from_id.large_name)))
                        break
        elif values.has_key('final_day') and not values.has_key('start_day') and self.start_day:
            duration = self.get_date_diff(self.start_day, values['final_day'])
            if self.get_date_diff(self.start_day, values['final_day']) <= 0:
                raise ValidationError(_('The Start Date should be equal to or less than Final Date.'))
            else:
                if self.get_date_diff(values['final_day'], self.project_id.final_day) <= 0:
                    raise ValidationError(_("The Final Date should be equal to or less than Project's Final Date."))
        elif not values.has_key('start_day') and not values.has_key('final_day') and self.start_day and self.final_day:
            duration = self.get_date_diff(self.start_day, self.final_day)
            if self.get_date_diff(self.start_day, self.final_day) <= 0:
                raise ValidationError(_('The Start Date should be equal to or less than Final Date.'))

        values['name'] = name + '(' + str(duration) + ')'
        return super(Process, self).write(values)
    
class ProcessTransition(models.Model):
    _name='montecarlo.process.transition'
    
    name = fields.Char('Description')
    process_from_id = fields.Many2one('montecarlo.process', 'Previous Process', required=True, ondelete="cascade")
    process_to_id = fields.Many2one('montecarlo.process', 'Next Process', required=True, ondelete="cascade")
    
    process_from_start_day = fields.Date(related='process_from_id.start_day', string='Start Date')
    process_from_final_day = fields.Date(related='process_from_id.final_day', string='Finish Date')
    process_from_probability = fields.Float(related='process_from_id.probability_success', string='Probability Success(%)')
    
    process_to_start_day = fields.Date(related='process_to_id.start_day', string='Start Date')
    process_to_final_day = fields.Date(related='process_to_id.final_day', string='Finish Date')
    process_to_probability = fields.Float(related='process_to_id.probability_success', string='Probability Success(%)')
    
    @api.multi
    def _compute_name(self):
        for trans in self:
            if trans.process_from_id:
                trans.name = 't = ' + str(trans.process_from_id.duration)