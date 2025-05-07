# -*- coding: utf-8 -*-
# from odoo import http


# class Parcotech(http.Controller):
#     @http.route('/parcotech/parcotech', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/parcotech/parcotech/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('parcotech.listing', {
#             'root': '/parcotech/parcotech',
#             'objects': http.request.env['parcotech.parcotech'].search([]),
#         })

#     @http.route('/parcotech/parcotech/objects/<model("parcotech.parcotech"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('parcotech.object', {
#             'object': obj
#         })

