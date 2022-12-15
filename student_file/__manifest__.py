# -*- coding: utf-8 -*-
# Copyright 2017 Juan D. Salcedo Salazar, salcedo.salazar@gmail.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Ficha Estudiante',
    'version': '1.0.1',
    'author': 'Salcedo Salazar Juan Diego',
    'summary': 'Ficha de registro de estudiante y registro de inidencias.',
    'description': """

Ficha de Estudiante.
===================================================
Este módulo permite registrar un estudiante y las incidencias relacionadas a este.
    """,
    'depends': [
        'base',
    ],
    'external_dependencies': {
    },
    'data': [
        'security/student_file_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/student_file_menuitem.xml',
        'views/student_file_view.xml',
        'views/incidence_file_view.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}