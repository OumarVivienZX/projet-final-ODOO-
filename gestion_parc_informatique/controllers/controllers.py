# -*- coding: utf-8 -*-
# from odoo import http


# class GestionParcInformatique(http.Controller):
#     @http.route('/gestion_parc_informatique/gestion_parc_informatique', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gestion_parc_informatique/gestion_parc_informatique/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('gestion_parc_informatique.listing', {
#             'root': '/gestion_parc_informatique/gestion_parc_informatique',
#             'objects': http.request.env['gestion_parc_informatique.gestion_parc_informatique'].search([]),
#         })

#     @http.route('/gestion_parc_informatique/gestion_parc_informatique/objects/<model("gestion_parc_informatique.gestion_parc_informatique"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gestion_parc_informatique.object', {
#             'object': obj
#         })

