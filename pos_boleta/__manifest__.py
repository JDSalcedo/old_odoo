# -*- coding: utf-8 -*-
# Copyright 2017 Juan D. Salcedo Salazar, salcedo.salazar@gmail.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Boleta POS',
    'version': '1.0.1',
    'author': 'Salcedo Salazar Juan Diego',
    'category': 'Point Of Sale',
    'summary': 'Boleta para el Punto de Venta',
    'description': """

Extensión del módulo Point of Sale.
====================================
Este módulo permite emitir un diario adicional para el Punto de Venta.

Principales funciones
----------------------
* Emisión de Boletas de Venta.
    """,
    'depends': [
        'base',
        'point_of_sale', 
        'account', 
        'report',
        'l10n_pe_amount_to_text',
    ],
    'data': [
        'views/pos_boleta_templates.xml',
        'views/pos_config_view.xml',
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
        'views/report_pre_invoice.xml',
        'views/report_pre_invoice_sigv.xml',
        'views/report_pre_invoice_boleta.xml',
        'views/report_invoice.xml',
        'views/report_invoice_boleta.xml',
        'views/account_report.xml',
        'views/account_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
