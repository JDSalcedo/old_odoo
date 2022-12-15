# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from criticalpath import Node
import logging

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _name='montecarlo.project'
    
    name = fields.Char('Name', required=True)
    start_day = fields.Date('Start Date')
    final_day = fields.Date('Finish Date')
    sprints_ids = fields.One2many('montecarlo.sprint', 'project_id', string='Sprints')
    count_sprints = fields.Integer('Sprints #', compute='_compute_count_sprints')
    criticalpath = fields.Text('Path')
    criticalpath_duration = fields.Integer('Duration(days)')
    description = fields.Text('Description')
    client_tolerance = fields.Integer('Client Tolerance(days)')
    
    processes_ids = fields.One2many('montecarlo.process', 'project_id', string='Process')
    count_processes = fields.Integer('Process #', compute='_compute_count_process')
    
    @api.constrains('client_tolerance')
    def _check_client_tolerance(self):
        if self.client_tolerance < 0:
            raise ValidationError('The Client tolerance must be positive or zero.')
    
    @api.onchange('start_day')
    def _onchange_start_day(self):
        warning = {}
        if self.start_day and self.final_day:
            sd = datetime.strptime(self.start_day, DF)
            fd = datetime.strptime(self.final_day, DF)
            if ((fd - sd).days + 1) <= 0:
                warning = {
                    'title': _("Warning for Start Date"),
                    'message': _("The Start Date should be equal to or less than Final Date.")
                    }
        res = {}
        if warning:
            res['warning'] = warning
            self.start_day = False
        return res
        
    @api.onchange('final_day')
    def _onchange_final_day(self):
        warning = {}
        if self.final_day and self.start_day:
            sd = datetime.strptime(self.start_day, DF)
            fd = datetime.strptime(self.final_day, DF)
            if ((fd - sd).days + 1 ) <= 0:
                warning = {
                    'title': _("Warning for Final Date"),
                    'message': _("The Final Date should be equal to or greater than Start Date.")
                    }
        res = {}
        if warning:
            res['warning'] = warning
            self.final_day = False
        return res
    
    @api.one
    @api.depends('sprints_ids')
    def _compute_count_sprints(self):
        if self.sprints_ids:
            self.count_sprints = len(self.sprints_ids.ids)
        else:
            self.count_sprints = 0
            
    @api.one
    @api.depends('processes_ids')
    def _compute_count_process(self):
        if self.processes_ids:
            self.count_processes = len(self.processes_ids.ids)
        else:
            self.count_processes = 0
    
    @api.one
    @api.depends('sprints_ids')
    def _compute_criticalpath(self):
        cad = ''
        ws = 0
        for sprint in self.sprints_ids:
            if sprint.criticalpath:
                cad = cad + sprint.criticalpath + u' '
            if sprint.criticalpath_duration:
                ws = ws + sprint.criticalpath_duration
        self.criticalpath = cad
        self.criticalpath_duration = ws
    
    @api.multi
    def show_sprints(self):
        self.ensure_one()

        sprints = self.mapped('sprints_ids')
        view_mode = 'kanban,tree,form,diagram'
        view_tree_id = self.env.ref('montecarlo.montecarlo_sprint_tree_view_b').id
        view_form_id = self.env.ref('montecarlo.montecarlo_sprint_form_view').id
        view_diagram_id = self.env.ref('montecarlo.montecarlo_sprint_diagram_view').id
        view_kanban_id = self.env.ref('montecarlo.montecarlo_sprint_kanban_view').id
        
        res_id = False
        domain = [('project_id','=',self.id)]
        context = {'default_project_id': self.id}
        if len(sprints) >= 1:
            domain = [('id', 'in', sprints.ids),('project_id','=',self.id)]

        return {
            'name': u"Sprints",
            'type': 'ir.actions.act_window',
            'view_mode': view_mode,
            'res_model': 'montecarlo.sprint',
            'target': 'self',
            'views': [(view_kanban_id, 'kanban'),
                      (view_tree_id, 'tree'),
                      (view_form_id, 'form'),
                      (view_diagram_id, 'diagram')],
            'view_id': view_tree_id,
            'res_id': res_id,
            'domain': domain,
            'context': context,
        }
    
    @api.multi
    def show_processes(self):
        self.ensure_one()

        processes = self.mapped('processes_ids')
        view_mode = 'tree,form'
        view_tree_id = self.env.ref('montecarlo.montecarlo_process_tree_view').id
        view_form_id = self.env.ref('montecarlo.montecarlo_process_form_view').id
        
        res_id = False
        domain = [('project_id','=',self.id)]
        context = {'default_project_id': self.id}
        if len(processes) >= 1:
            domain = [('id', 'in', processes.ids),('project_id','=',self.id)]

        return {
            'name': u"Processes",
            'type': 'ir.actions.act_window',
            'view_mode': view_mode,
            'res_model': 'montecarlo.process',
            'target': 'self',
            'views': [(view_tree_id, 'tree'),
                      (view_form_id, 'form')],
            'view_id': view_tree_id,
            'res_id': res_id,
            'domain': domain,
            'context': context,
        }
        
    @api.multi
    def show_results(self):
        self.ensure_one()
        
        view_mode = 'kanban,tree,pivot,graph'
        view_tree_id = self.env.ref('montecarlo.montecarlo_project_result_tree').id
        view_pivot_id = self.env.ref('montecarlo.montecarlo_project_result_pivot').id
        view_graph_id = self.env.ref('montecarlo.montecarlo_project_result_graph').id
        view_kanban_id = self.env.ref('montecarlo.montecarlo_project_result_kanban').id
        
        #context = {'search_default_thisday': 1,}

        return {
            'res_id': False,
            'name': u"Simulation Statistics",
            'type': 'ir.actions.act_window',
            'view_mode': view_mode,
            'res_model': 'montecarlo.project.result',
            'target': 'self',
            'views': [(view_kanban_id, 'kanban'),
                      (view_tree_id, 'tree'),
                      (view_pivot_id, 'pivot'),
                      (view_graph_id, 'graph')],
            'view_id': False,
            'context': {},
            'domain': [('project_id','=',self.id)],
        }
        
    @api.model
    def create(self, values):
        project = super(Project, self).create(values)
        
        vals = {
                'project_id': project.id,
                'start': False,
                'probability_success': 100.0
            }
        
        large_name_list = [
            '1) Creación de la visión del Proyecto.',
            '2) Identificación del Scrum Master y Socio(s).',
            '3) Formación de equipos Scrum.',
            '4) Desarrollo de Épicas.',
            '5) Creación de la lista priorizada de pendientes del producto.',
            '6) Planificación de lanzamiento.',
            '7) Creación de Historias de Usuario.',
            '8) Aprobación, estimación y asignación de historias de usuario.',
            '9) Creación y estimación de tareas.',
            '10) Creación de la lista de pendientes del Sprint.',
            '11) Creación de entregables.',
            '12) Mantenimiento de la lista priorizada de pendientes del producto.',
            '13) Demostración y validación del Sprint.',
            '14) Retrospectiva del Sprint.',
            '15) Envio de entregables.',
            '16) Retrospectiva del Proyecto.'
        ]
        i = 1
        trans = {}
        for large_name in large_name_list:
            vals['large_name'] = large_name
            vals['start'] = True if i == 1 else False
            process = self.env['montecarlo.process'].create(vals)
            trans[i] = process.id
            i = i + 1 
        
        tvals = {}
        tvals[1] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16}
        tvals[2] = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
        tvals[3] = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16}
        tvals[4] = {5, 7}
        tvals[5] = {6, 7}
        tvals[6] = {10, 15}
        tvals[7] = {8, 9, 13}
        tvals[8] = {9}
        tvals[9] = {10}
        tvals[10] = {11, 12}
        tvals[11] = {13}
        tvals[12] = {13}
        tvals[13] = {14, 15}
        tvals[14] = {}
        tvals[15] = {}
        tvals[16] = {}
        
        for from_id in tvals:
            for to_id in tvals[from_id]:
                self.env['montecarlo.process.transition'].create({'process_from_id':trans[from_id], 'process_to_id': trans[to_id]})
        
        return project
    
    def get_criticalpath_project(self, act_ids):
        p = Node('project')
        node = {}
        #Node register
        for act in act_ids:
            node[act.id] = p.add(Node(act.name, duration = act.duration))
        #Link Nodes
        for act in act_ids:
            for trans in act.to_ids:
                p.link(node[trans.process_from_id.id], node[trans.process_to_id.id])
        
        p.update_all()
        
        return p, node
        
    @api.multi
    def critical_path(self):
        
        self.ensure_one()

        if not self.processes_ids:
            raise UserError(_("The Critical Path Method cannot be started. There are no processes in the Project: %s" %(self.name)))
        else:
            proceses_without_days = self.processes_ids.search(['&',('project_id','=', self.id),'|',('start_day','=', False),('final_day','=', False)])
            if proceses_without_days:
                raise ValidationError(_("The Critical Path Method cannot be started. There are processes without Dates."))

        has_start = False

        for process in self.processes_ids:
            if process.start:
                has_start = True

        if not has_start:
            raise UserError(_("The Critical Path Method cannot be started. It does not have any starting process. Modify Project: %s processes to mark one as the starting point." %(self.name)))
        
        p, node = self.get_criticalpath_project(self.processes_ids)
        
        for act in self.processes_ids:
            act.earliest_start = node[act.id].es
            act.earliest_finish = node[act.id].ef
            act.lastest_start = node[act.id].ls
            act.lastest_finish = node[act.id].lf
            act.slack = node[act.id].lf - node[act.id].ef
        
        self.criticalpath = str(p.get_critical_path()).decode('utf-8')
        self.criticalpath_duration = p.duration
