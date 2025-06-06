from odoo import api, fields, models
import logging
from odoo.exceptions import ValidationError, UserError, MissingError

class RayAdmin(models.Model):
    _name = "ray.admin"
    _inherit = ['mail.thread']
    _description = "Administradores"
    _inherits = {
        'res.partner': 'partner_id'
    }
    active = fields.Boolean(
        string="Activo",
        tracking=True,
        default=True
    )

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        tracking=True
    )
    user_id = fields.Many2one(
        string="Usuario Odoo",
        comodel_name="res.users",
        tracking=True
    )
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
    email = fields.Char(
        string="Email",
        tracking=True,
        related="partner_id.email"
    )
    firebase_uid = fields.Char(
        string="UID de Firebase",
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

    admin_type = fields.Selection(
        string="Tipo de Administrador",
        selection=[
            ('parent', 'Padre'),
            ('child', 'Hijo')
        ],
        required=True,
        tracking=True
    )
    created_by_id = fields.Many2one(
        string="Creado por",
        comodel_name="ray.admin"
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

    def get_data(self):
        data = {
            'admin_type': self.admin_type if self.admin_type else '',
            'id': self.id,
            'active': self.active,
            'state': self.state if self.state else '',
            'name': self.name if self.name else '',
            'last_name': self.last_name if self.last_name else '',
            'email': self.email if self.email else '',
            'firebase_uid': self.firebase_uid if self.firebase_uid else '',
            'institution': self.institution_id.get_data(),
            'rayiot_ids': [rayiot.id for rayiot in self.rayiot_ids],
            'created_by_id': self.created_by_id.id if self.created_by_id else 0
        }
        return data

    @api.model
    def get_admin_by_email(self, email):
        if not email:
            return {
                'success': False,
                'message': 'El email es requerido'
            }

        admin = self.env['ray.admin'].sudo().search([
            ('email', '=', email)
        ], limit=1)

        if not admin:
            return {
                'success': False,
                'message': 'No hemos encontrado al administrador deseado intenta de nuevo'
            }

        if admin.state == 'pending':
            return {
                'success': False,
                'message': 'El administrador aún no ha sido autorizado por uno de nuestros agentes'
            }

        return {
            'success': True,
            'data': admin.get_data(),
            'message': 'Administrador concedido'
        }

    @api.model
    def create_admin_pending_verification(self, **vals):

        if not vals['email'] or not vals['firebase_uid'] or not vals['institution_id'] or not vals['name'] or not vals['last_name']:
            return {
                'success': False,
                'message': 'Todos los campos son obligatorios'
            }

        user_exists = self.env['res.users'].with_context(mail_auto_subscribe_no_notify=True).search([
            ('login', '=', vals['email'])
        ])

        logging.info(f'user_exists {user_exists}')
        if user_exists:
            return {
                'success': False,
                'message': 'El administrador ya existe'
            }

        user = self.env['res.users'].with_context(mail_auto_subscribe_no_notify=True).create({
            'login': vals['email'],
            'name': vals['email'],
            'sel_groups_1_9_10': '9'
        })
        user.partner_id.write({'email': vals['email']})

        ray_admin = self.env['ray.admin'].create({
            'partner_id': user.partner_id.id,
            'user_id': user.id,
            'firebase_uid': vals['firebase_uid'],
            'state': 'pending',
            'institution_id': vals['institution_id'],
            'name': vals['name'],
            'last_name': vals['last_name']
        })

        response = {
            'success': True,
            'data': ray_admin.get_data()
        }

        return response

    def authorize_admin_by_admin(self, admin_id):
        if not admin_id:
            return {
                'success': False,
                'message': 'Es necesario proporcionar al administrador que deseas aceptar'
            }

        admin = self.env['ray.admin'].sudo().browse(admin_id)

        if not admin:
            return {
                'success': False,
                'message': 'No hemos encontrado al administrador que deseas autorizar'
            }

        if admin.institution_id.id == self.institution_id.id:
            admin.admin_type = 'child'
            admin.state = 'active'
            admin.created_by_id = self.id

        return {
            'success': True,
            'data': admin.get_data()
        }

    def delete_admin(self):
        self.ensure_one()
        if not self.exists():
            return {
                'success': False,
                'message': 'El administrador proporcionado no existe'
            }

        self.write({
            'active': False
        })

        return {
            'success': True,
            'message': 'Haz eliminado el usuario correctamente'
        }
