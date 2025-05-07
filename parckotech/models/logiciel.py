# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Logiciel(models.Model):
    _name = 'parckotech.logiciel'
    _description = 'Logiciel'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nom', required=True, tracking=True)
    version = fields.Char('Version', tracking=True)
    editeur = fields.Char('Éditeur', tracking=True)
    license_key = fields.Char('Clé licence', tracking=True)        # ➕ nouveau

    pack_id = fields.Many2one('parckotech.pack.informatique', string='Pack',
                              required=True, tracking=True)
    client_id = fields.Many2one('res.partner', related='pack_id.client_id',
                                store=True, string='Client')
    site_id = fields.Many2one('parckotech.site.client', related='pack_id.site_id',
                              store=True, string='Site')

    materiel_ids = fields.Many2many('parckotech.materiel', string='Matériels')
    licence_ids = fields.One2many('parckotech.licence.logicielle', 'logiciel_id',
                                  string='Licences')
    licence_count = fields.Integer(compute='_compute_licence_count',
                                   string='Nombre de licences')

    description = fields.Text('Description')
    notes = fields.Text('Notes')
    active = fields.Boolean(default=True)

    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')

    @api.depends('licence_ids')
    def _compute_licence_count(self):
        for logiciel in self:
            logiciel.licence_count = len(logiciel.licence_ids)
