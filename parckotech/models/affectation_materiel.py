# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AffectationMateriel(models.Model):
    _name = 'parckotech.affectation.materiel'
    _description = 'Affectation de Matériel'
    _order = 'date_debut desc'

    name = fields.Char(compute='_compute_name', store=True)

    materiel_id = fields.Many2one('parckotech.materiel', required=True,
                                  ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', required=True)

    date_debut = fields.Date(default=fields.Date.today, required=True)
    date_fin = fields.Date()
    site_id = fields.Many2one('parckotech.site.client', required=True)

    notes = fields.Text()
    active = fields.Boolean(default=True)

    # ---------- helpers ----------
    @api.depends('materiel_id', 'employee_id', 'date_debut')
    def _compute_name(self):
        for rec in self:
            rec.name = (f"{rec.materiel_id.name} - {rec.employee_id.name}"
                        f" ({rec.date_debut})") if rec.materiel_id else "Nouvelle affectation"

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec.materiel_id.employee_id = rec.employee_id
        return recs

    def write(self, vals):
        res = super().write(vals)
        if 'employee_id' in vals:
            for rec in self:
                rec.materiel_id.employee_id = rec.employee_id
        return res
