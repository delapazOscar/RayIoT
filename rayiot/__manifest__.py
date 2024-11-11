{
    'name': 'RayIoT Management System',
    'author': 'Oscar de la Paz',
    'website': 'https://www.instagram.com/emprendimientotecgdl/',
    'summary': 'Odoo 16 development',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/ray_event.xml',
        'views/ray_rayiot.xml',
        'views/ray_institution.xml',
        'views/ray_admin.xml',
        'views/ray_institution_location.xml'

    ],
    'application': True,
    'sequence': -10,
    "images": [
        'static/rayiot.png'
    ]
}
