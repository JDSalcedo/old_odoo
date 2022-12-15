# -*- coding: utf-8 -*-
# Copyright (C) 2018 Juan D. Salcedo Salazar <salcedo.salazar@gmail.com>
{
    'name': "Crédito - Validación de Ventas",
    'summary': """
        Crédito Cliente y validación de ventas.""",

    'description': """
        Este módulo permite registrar un límite de crédito 
        para cada cliente y validar las ventas que se le realizan.
    """,

    'author': "Salcedo Salazar Juan Diego",
    'version': '0.1',
    'depends': [
        'base',
        'sale',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/approve_mail_template.xml',
        'data/refuse_mail_template.xml',
        'wizard/sale_order_refuse_wizard_view.xml',
        'views/res_company_view.xml',
        'views/res_config_views.xml',
        'wizard/credit_limit_update_view.xml',
        'views/res_partner_view.xml',
        'views/sale_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}