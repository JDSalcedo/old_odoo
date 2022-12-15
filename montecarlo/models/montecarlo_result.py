# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProjectResult(models.Model):
    _name = 'montecarlo.project.result'
    
    place = fields.Integer('Place', default=0)
    project_id = fields.Many2one('montecarlo.project', string='Project')
    iterations = fields.Integer('Iterations')
    success_cases = fields.Integer('Success cases')
    viability = fields.Float('Viability %')
    result_date = fields.Date('Result Date')
    result_time = fields.Char('Result Time')
    execution_time = fields.Float('Execution Time(seg)')
    category  = fields.Selection([
            ('no_viable','No Viable'),
            ('mod_viable','Moderately Viable'),
            ('viable','Viable'),
        ], index=True)