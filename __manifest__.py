# -*- coding: utf-8 -*-
{
    'name': "Módulo de Movilidad",

    'summary': """Módulo de movilidad para GCBA""",

    'description': """
        Módulo de movilidad para GCBA - MAYEP
    """,

    'author': "PersiscalConsulting LLC.",
    'website': "https://persiscalconsulting.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_holidays'],

    # always loaded
    'data': [
        'views/movilidad.xml',
        'views/categoria.xml',
        'security/ir.model.access.csv',
        #'reports/personal_report.xml',
        #'reports/movilidad_report.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo.xml',
    # ],

    'application' : True,

    #'images': ['static/description/icon.png'],
}
