from odoo import api, fields, models
import logging

class Event(models.Model):
    _name = "ray.event"
    _inherit = ['mail.thread']
    _description = "Eventos RayIoT"

    name = fields.Char(
        string='Nombre del evento',
        tracking=True,
        required=True
    )

    description = fields.Char(
        string='Descripción del evento',
        tracking=True
    )

    date = fields.Datetime(
        string='Fecha',
        tracking=True
    )