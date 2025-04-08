{
    'name': 'Real Estate',
    'version': '18.0.0.1',
    'summary': 'Real Estate Advertisement Module',
    'description': """
        This module manages real estate properties with features such as property details,
        availability dates, pricing, and offers.
    """,
    'category': 'Customization',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_menus.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_view.xml',
        'views/estate_property_tag_view.xml',
        'views/estate_property_offer_view.xml',
        'views/res_user.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3'
}
