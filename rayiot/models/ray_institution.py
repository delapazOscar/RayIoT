from odoo import api, fields, models
import logging

class RayInstitution(models.Model):
    _name = "ray.institution"
    _inherit = ['mail.thread']
    _description = "Instituciones"

    active = fields.Boolean(
        string="Activo",
        default=True,
        tracking=True
    )
    name = fields.Char(
        string="Nombre de la Escuela",
        required=True,
        tracking=True
    )
    institution_type = fields.Selection(
        [('school', 'Escuela'), ('company', 'Empresa')],
        string="Tipo de institución",
        tracking=True
    )
    school_type = fields.Selection(
        [('public', 'Pública'), ('private', 'Privada')],
        string="Tipo de Escuela",
        required=True,
        tracking=True
    )
    address = fields.Char(
        string="Dirección",
        tracking=True
    )
    city = fields.Char(
        string="Ciudad",
        tracking=True,
        required=True
    )
    state_id = fields.Many2one(
        'res.country.state',
        string="Estado",
        domain=[('country_id.code', '=', 'MX')],
        tracking=True,
        required=True
    )
    educational_level = fields.Selection(
        [('preschool', 'Preescolar'),
         ('primary', 'Primaria'),
         ('secondary', 'Secundaria'),
         ('high_school', 'Bachillerato'),
         ('university', 'Universidad')],
        string="Nivel Educativo",
        tracking=True
    )

    def get_data(self):
        data = {
            'id': self.id if self.id else 0,
            'active': self.active,
            'name': self.name if self.name else '',
            'institution_type': self.institution_type if self.institution_type else '',
            'school_type': self.school_type if self.school_type else '',
            'address': self.address if self.address else '',
            'city': self.city if self.city else '',
            'state': {
                'id': self.state_id.id if self.state_id.id else 0,
                'name': self.state_id.name if self.state_id.name else ''
            },
            'education_level': self.educational_level if self.educational_level else ''
        }

        return data
