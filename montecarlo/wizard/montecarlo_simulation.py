# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from pytz import timezone
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

try:
    import numpy.random
except ImportError:
    numpy = None

import logging

_logger = logging.getLogger(__name__)


class SimulationWizard(models.TransientModel):
    _name = 'montecarlo.simulation.wizard'
    
    iterations = fields.Integer('Iterations', default=10000, help='Number of iterations for Monte Carlo Simulation')
    project_id = fields.Many2one('montecarlo.project', string='Project')
    sprints_ids = fields.One2many('montecarlo.sprint', related='project_id.sprints_ids', string="Sprints")
    simulation_date = fields.Datetime('Date', default=fields.Datetime.now)
    
    processes_ids = fields.One2many('montecarlo.process', related='project_id.processes_ids', string='Processes')
    
    '''
    def bfs(self, graph, start):
        visited, queue = set(), [start]
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                queue.extend(graph[vertex].get('to_acts') - visited)
        return visited
    '''
    
    def eval_probability(self, node):
        return numpy.random.choice([True, False], 1, p=[node['ps']/100, 1 - (node['ps']/100)])[0]
    
    def simulate(self, graph, start, tolerance):
        visited, queue = set(), [start]
        days, delay = -1, 0
        while queue:
            days = days + 1
            li_pop = []
            for act in queue:
                #If the day is not greatter than the earliest finish then 'continue'
                if days < graph[act]['ef']:
                    continue
                #The day should be between the earliest finish and the lastest finish ['ef' <= days <= 'lf']
                elif days >= graph[act]['ef'] and days <= graph[act]['lf']:
                    if self.eval_probability(graph[act]):
                        li_pop.append(act)
                elif days > graph[act]['lf']:
                    if tolerance > 0:
                        delay = delay + 1
                        if self.eval_probability(graph[act]):
                            li_pop.append(act)
                    else:
                        return visited, delay
            
            for act in li_pop:
                vertex = act
                queue.remove(vertex)
                if vertex not in visited:
                    visited.add(vertex)
                    temp = graph[vertex]['to_acts'] - visited
                    for n in temp:
                        # The new activity can't be add to the queue 
                        # if its predecessors are not visited
                        if graph[n]['from_acts'].issubset(visited):
                            queue.append(n)
        return visited, delay
    
    def evaluate_simulation(self, graph, start, tolerance):
        visited, delay = self.simulate(graph, start, tolerance)
        graph_size = len(graph)
        if graph_size == len(visited):
            if tolerance > 0:
                if delay <= tolerance:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False
    
    @api.multi
    def mc_simulation(self):
        self.ensure_one()
        
        processes = self.project_id.processes_ids
        li_graph = []
        
        if not processes:
            raise UserError(_("The Monte Carlo simulation cannot be started. There are no Processes."))
        
        #Ensure the critical path is already to every sprint
        self.project_id.critical_path()

        #building graph
        graph = {}
        
        for act in self.project_id.processes_ids:
            graph[act.id] = {'ef' : act.earliest_finish,
                             'lf' : act.lastest_finish,
                             'ps' : act.probability_success,
                             'to_acts' : set(),
                             'from_acts' : set()
                            }
            for trans in act.to_ids:
                graph[act.id]['to_acts'].add(trans.process_to_id.id)
            for p_trans in act.from_ids:
                graph[act.id]['from_acts'].add(p_trans.process_from_id.id)

        starts = self.project_id.processes_ids.search_read([('start','=',True),('project_id','=',self.project_id.id)],['id'])
        #If there are multiples nodes to start
        if len(starts) > 1:
            graph['s'] = {'ef' : 0,
                          'lf' : 0,
                          'ps' : 100,
                          'to_acts' : set(),
                          'from_acts' : set()
                          }
            for s in starts:
                graph['s']['to_acts'].add(s['id'])
                graph[s['id']]['from_acts'].add('s')
                
            li_graph.append({'id': self.project_id.id, 'graph': graph, 'start': 's', 'tolerance': self.project_id.client_tolerance})
        elif len(starts) == 1:
            li_graph.append({'id': self.project_id.id, 'graph': graph, 'start': starts[0]['id'], 'tolerance': self.project_id.client_tolerance})
        
        sccs = 0
        sd = {}
        stime = time.time()
        for i in range(self.iterations):
            success = True
            for g in li_graph:
                eval = self.evaluate_simulation(g['graph'], g['start'], g['tolerance'])
                if not eval:
                    success = False
                else:
                    if g['id'] in sd:
                        sd[g['id']] = sd[g['id']] + 1
                    else:
                        sd[g['id']] = 1
                                   
            if success:
                sccs = sccs + 1
        ftime = time.time()
        #_logger.info(ftime - stime)
        #_logger.info(sccs)
        #_logger.info((float(sccs) / self.iterations)*100)
        
        #for d in sd:
        #    _logger.info(sd[d])
        
        tz = 'America/Lima'
        if self.env.user.tz:
            tz = self.env.user.tz
        date_obj = datetime.strptime(self.simulation_date, DTF)
        date_utc_timezone = timezone('UTC').localize(date_obj)
        date_astimezone = date_utc_timezone.astimezone(timezone(tz))
        date_astimezone_str = date_astimezone.strftime(DTF)
        
        viability = (float(sccs) / self.iterations)*100.00
        
        category = 'no_viable'
        if viability > 75:
            category = 'viable'
        elif viability > 59:
            category = 'mod_viable'
            
        vals = {
            'project_id': self.project_id.id,
            'iterations': self.iterations,
            'success_cases': sccs,
            'viability': viability,
            'result_date': date_astimezone_str[:10],
            'result_time': date_astimezone_str[11:],
            'execution_time': ftime - stime,
            'category': category,
            }
        
        place = self.env['montecarlo.project.result'].search_read([('project_id','=',self.project_id.id)], ['place'], limit=1, order="id desc")
        
        vals['place'] = place[0]['place'] + 1 if len(place) > 0 else 0
        
        res_id = self.env['montecarlo.project.result'].create(vals)
        
        view_mode = 'tree,pivot'
        view_tree_id = self.env.ref('montecarlo.montecarlo_project_result_tree').id
        view_pivot_id = self.env.ref('montecarlo.montecarlo_project_result_pivot').id

        search_id = self.env.ref('montecarlo.montecarlo_project_result_search').id
        context = {}

        return {
            'res_id': res_id.id,
            'name': u"Projects Statistics",
            'type': 'ir.actions.act_window',
            'view_mode': view_mode,
            'res_model': 'montecarlo.project.result',
            'target': 'self',
            'views': [(view_tree_id, 'tree'),
                      (view_pivot_id, 'pivot')],
            'view_id': False,
            'context': context,
            'domain': [('id','=',res_id.id)],
            'search_view_id': search_id,
        }