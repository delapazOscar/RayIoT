from odoo import api, fields, models
import logging

class RayAdmin(models.Model):
    _name = "ray.admin"
    _inherit = ['mail.thread']
    _description = "Administradores"

    active = fields.Boolean(
        string="Activo",
        default=True,
        tracking=True
    )
    name = fields.Char(
        string="Nombre",
        required=True,
        tracking=True
    )
    last_name = fields.Char(
        string="Apellido",
        required=True,
        tracking=True
    )
    institution_id = fields.Many2one(
        string="Institución",
        comodel_name="ray.institution",
        required=True,
        tracking=True
    )
    rayiot_ids = fields.Many2many(
        string="Dispositivos RayIoT",
        comodel_name="ray.rayiot"
    )
    state = fields.Selection(
        string="Estado",
        selection=[
            ('pending', 'Pendiente'),
            ('active', 'Activo')
        ],
        default="pending",
        tracking=True,
        readonly=True
    )

    def name_get(self):
        res = []
        for record in self:
            name = f"{record.name or ''} {record.last_name or ''}".strip()
            res.append((record.id, name))
        return res

    @api.model
    def create(self, vals):
        admin = super(RayAdmin, self).create(vals)
        return admin

    def action_authorize_admin(self):
        self.state = 'active'
