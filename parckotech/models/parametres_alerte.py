# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ParametreAlerte(models.Model):
    _name = 'parckotech.parametre.alerte'
    _description = "Paramètres d'alerte"

    name = fields.Char('Nom', required=True)

    type_alerte = fields.Selection([
        ('garantie', 'Garantie'),
        ('licence', 'Licence'),
        ('maintenance', 'Maintenance'),
        ('contrat', 'Contrat')
    ], string='Type d’alerte', required=True)

    frequence = fields.Selection([
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('once', 'Unique')
    ], string='Fréquence', default='weekly', required=True)

    jours_avant_expiration = fields.Integer('Jours avant expiration', default=30)
    actif = fields.Boolean('Actif', default=True)

    user_ids = fields.Many2many(
        'res.users', 'parckotech_alerte_user_rel', 'alerte_id', 'user_id',
        string='Utilisateurs notifiés'
    )
    client_id = fields.Many2one(
        'res.partner', string='Client spécifique',
        domain=[('is_company', '=', True), ('is_it_client', '=', True)]
    )
    global_alert = fields.Boolean(
        'Alerte globale', default=True,
        help="Si coché, s’applique à tous les clients"
    )

    message_personnalise = fields.Text('Message personnalisé')