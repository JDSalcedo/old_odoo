# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from criticalpath import Node
import logging

_logger = logging.getLogger(__name__)


class Sprint(models.Model):
    _name='montecarlo.sprint'
    _order='sequence'
    
    name = fields.Char('Name', required=True)
    sequence = fields.Integer(default=10,
        help="Gives the sequence of this sprint when displaying the project.")
    activities_ids = fields.One2many('montecarlo.activity', 'sprint_id', string='Activities')
    project_id = fields.Many2one('montecarlo.project', 'Project', required=True)
    count_activities = fields.Integer('Activities #', compute='_compute_count_activities')
    criticalpath = fields.Text('Critical Path')
    criticalpath_duration = fields.Integer('Critical Path Duration(days)')
    client_tolerance = fields.Integer('Client Tolerance(days)', required=True,
                                      help='Client tolerance, how many days \
                                          the client can wait for sprint deliverance.')
    create_acts = fields.Integer('Create Activities', help='Number of activities to create automatically.',
                                 default=1)

    @api.one
    @api.depends('activities_ids')
    def _compute_count_activities(self):
        if self.activities_ids:
            self.count_activities = len(self.activities_ids.ids)
        else:
            self.count_activities = 0
    
    @api.multi
    def show_activities(self):
        self.ensure_one()

        activities = self.mapped('activities_ids')
        view_mode = 'tree,form'
        view_tree_id = self.env.ref('montecarlo.montecarlo_activity_tree_view').id
        view_form_id = self.env.ref('montecarlo.montecarlo_activity_form_view').id
        res_id = False
        domain = [('sprint_id','=',self.id)]
        context = {'default_sprint_id': self.id}
        if len(activities) >= 1:
            domain = [('id', 'in', activities.ids),('sprint_id','=',self.id)]

        return {
            'name': u"Activities",
            'type': 'ir.actions.act_window',
            'view_mode': view_mode,
            'res_model': 'montecarlo.activity',
            'target': 'self',
            'views': [(view_tree_id, 'tree'),
                      (view_form_id, 'form')],
            'view_id': view_tree_id,
            'res_id': res_id,
            'domain': domain,
            'context': context,
        }
    
    @api.multi
    def show_diagram(self):
        self.ensure_one()

        view_mode = 'diagram'
        view_diagram_id = self.env.ref('montecarlo.montecarlo_sprint_diagram_view').id
        res_id = False
        domain = [('id','=',self.id)]
        context = {}

        return {
            'name': u"Activities",
            'type': 'ir.actions.act_window',
            'view_mode': view_mode,
            'res_model': 'montecarlo.sprint',
            'target': 'self',
            'views': [(view_diagram_id, 'diagram')],
            'view_id': view_diagram_id,
            'res_id': res_id,
            'domain': domain,
            'context': context,
        }

    @api.multi
    def create_activities(self):
        self.ensure_one()
        
        if self.create_acts <= 0:
            raise UserError(_("This number must be positive"))
        
        last_id = self.env['montecarlo.activity'].search_read([], ['id'], limit=1, order="id desc")
        act = last_id[0]['id'] if len(last_id) > 0 else 0
        
        for i in range(self.create_acts):
            vals = {
                'large_name': ('Act #%s' % str(act + 1)),
                'sprint_id': self.id,
                'probability_success': 100.0,
                'duration': 0,
                }
            self.env['montecarlo.activity'].create(vals)
            act = act + 1
        self.create_acts = 0
        
    def get_criticalpath_project(self, act_ids):
        p = Node('project')
        node = {}
        #Node register
        for act in act_ids:
            node[act.id] = p.add(Node(act.name, duration = act.duration))
        #Link Nodes
        for act in act_ids:
            for trans in act.to_ids:
                p.link(node[trans.activity_from_id.id], node[trans.activity_to_id.id])
        
        p.update_all()
        
        return p, node
        
    @api.multi
    def critical_path(self):
        
        self.ensure_one()

        if not self.activities_ids:
            raise UserError(_("The Critical Path Method cannot be started. There are no activities in the Sprint: %s" %(self.name)))

        has_start = False

        for activity in self.activities_ids:
            if activity.start:
                has_start = True

        if not has_start:
            raise UserError(_("The Critical Path Method cannot be started. It does not have any starting activity. Modify Sprint: %s activities to mark one as the starting point." %(self.name)))
        
        p, node = self.get_criticalpath_project(self.activities_ids)
        
        for act in self.activities_ids:
            act.earliest_start = node[act.id].es
            act.earliest_finish = node[act.id].ef
            act.lastest_start = node[act.id].ls
            act.lastest_finish = node[act.id].lf
        
        self.criticalpath = str(p.get_critical_path()).decode('utf-8')
        self.criticalpath_duration = p.duration