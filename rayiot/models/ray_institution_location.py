from odoo import api, fields, models
import logging

class RayInstitutionLocation(models.Model):
    _name = "ray.institution.location"
    _inherit = ['mail.thread']
    _description = "Ubicaciones en instituciones"

    active = fields.Boolean(
        string="Activo",
        default=True,
        tracking=True
    )
    name = fields.Char(
        string="Ubicación dentro de institución",
        required=True,
        tracking=True
    )