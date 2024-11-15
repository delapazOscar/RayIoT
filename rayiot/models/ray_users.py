from odoo import api, fields, models
import logging
from odoo.exceptions import ValidationError, UserError, MissingError

class RayAdmin(models.Model):
    _name = "ray.user"
    _inherit = ['mail.thread']
    _description = "Usuarios"

    active = fields.Boolean(
        string="Activo",
        tracking=True,
        default=True
    )
    name = fields.Char(
        string="Nombre",
        required=True,
        tracking=True
    )
    last_name = fields.Char(
        string="Apellido",
        tracking=True
    )
    email = fields.Char(
        string="Email",
        tracking=True
    )
    institution_id = fields.Many2one(
        string="Institución",
        comodel_name="ray.institution",
        tracking=True
    )
    phone_number = fields.Char(
        string="Número telefónico",
        tracking=True
    )

