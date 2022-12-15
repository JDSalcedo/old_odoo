# -*- coding: utf-8 -*-
# Copyright 2017 Juan D. Salcedo Salazar, salcedo.salazar@gmail.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Monte Carlo(SCRUM)',
    'version': '1.0.1',
    'author': 'Salcedo Salazar Juan Diego',
    'summary': 'Simulación Monte Carlo aplicado a Proyectos SCRUM',
    'description': """

Simulación Monte Carlo aplicado a Proyectos SCRUM.
===================================================
Este módulo permite aplicar la Simulación de Monte Carlo a la Gestión de Proyectos bajo la Metodología SCRUM.
    """,
    'depends': [
        'base',
    ],
    'external_dependencies': {
        'python' : ['numpy.random'],
    },
    'data': [
        'security/montecarlo_security.xml',
        'security/ir.model.access.csv',
        'wizard/montecarlo_simulation_view.xml',
        'views/montecarlo_menuitem.xml',
        'views/montecarlo_view.xml',
        'views/montecarlo_result_view.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
