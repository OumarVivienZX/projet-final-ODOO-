# -*- coding: utf-8 -*-
from odoo import models, fields

class Client(models.Model):
    _name = 'gestion_parc.client'
    _description = 'Client'

    name = fields.Char(string='Nom', required=True)
    contact = fields.Char(string='Contact')
    address = fields.Text(string='Adresse')
    contrat_ids = fields.One2many('gestion_parc.contrat_infogerance', 'client_id', string='Contrats')
    equipement_ids = fields.One2many('gestion_parc.equipements', 'client_id', string='Équipements')

class ContratInfogerance(models.Model):
    _name = 'gestion_parc.contrat_infogerance'
    _description = 'Contrat d\'Infogérance'

    client_id = fields.Many2one('gestion_parc.client', string='Client', required=True)
    date_debut = fields.Date(string='Date de Début')
    date_fin = fields.Date(string='Date de Fin')
    frequence_facturation = fields.Char(string='Fréquence de Facturation')
    facture_ids = fields.One2many('gestion_parc.facture', 'contrat_id', string='Factures')
    equipement_ids = fields.Many2many('gestion_parc.equipements', string='Équipements')

class Equipements(models.Model):
    _name = 'gestion_parc.equipements'
    _description = 'Équipements'

    client_id = fields.Many2one('gestion_parc.client', string='Client', required=True)
    id_materiel = fields.Char(string='ID Matériel', required=True)
    type_de_materiel = fields.Char(string='Type de Matériel')
    marque = fields.Char(string='Marque')
    statut_materiel = fields.Char(string='Statut Matériel')
    date_acquisition = fields.Date(string='Date d\'Acquisition')
    fin_de_garantie = fields.Date(string='Fin de Garantie')
    ticket_ids = fields.One2many('gestion_parc.ticket', 'equipement_id', string='Tickets')
    contrat_ids = fields.Many2many('gestion_parc.contrat_infogerance', string='Contrats')

class Ticket(models.Model):
    _name = 'gestion_parc.ticket'
    _description = 'Ticket'

    equipement_id = fields.Many2one('gestion_parc.equipements', string='Équipement', required=True)
    id_ticket = fields.Char(string='ID Ticket', required=True)
    description = fields.Text(string='Description')
    statut = fields.Char(string='Statut')
    date_creation = fields.Date(string='Date de Création')

class Facture(models.Model):
    _name = 'gestion_parc.facture'
    _description = 'Facture'

    contrat_id = fields.Many2one('gestion_parc.contrat_infogerance', string='Contrat', required=True)
    id_facture = fields.Char(string='ID Facture', required=True)
    montant = fields.Float(string='Montant')
    date_emission = fields.Date(string='Date d\'Émission')

