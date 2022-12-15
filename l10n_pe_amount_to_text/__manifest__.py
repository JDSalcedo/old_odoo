
# -*- encoding: utf-8 -*-
###########################################################################
#    Copyright (c) 2013 AACONSULTING - http://www.consulting-sac.com.pe/
#    All Rights Reserved.
#    info AACONSULTING (info@consulting-sac.com.pe)
############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name' : "l10n_pe_amount_to_text",
    'version' : "1.1",
    'depends' : [
        'base',
        'account',
    ],
    'author' : "Softlab Perú SAC",
    'category' : "Localization/Peru",
    'description' : """Modulo para agregar el monto en texto customizado para implantación de versión 10.0 de ODOO
    """,
    'website' : "http://www.softlabperu.com",
    'license' : "AGPL-3",
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : [
    ],
    'data': [
        'views/account_invoice_view.xml',
        'views/res_currency_view.xml',
    ],
    'installable' : True,
    'active' : False,
}