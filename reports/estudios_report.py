# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.tools.float_utils import float_round as round
import math
import copy
import logging
_logger = logging.getLogger(__name__)

class EstudiosReport(models.AbstractModel):

    _name = 'report.puntoingreso.report_estudios_data'


    @api.multi
    #@api.one
    @api.model

    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('puntoingreso.report_estudios_data')


        pacientes = self.env['puntoingreso.service'].search([('id', 'in', docids)], order="patient_ids").mapped('patient_ids')

        fechas = []
        resumen = []
        estudio_paciente = []
        gastos = []
        honors = []
        gastos_por = 0
        honors_por = 0
        tarifa = 0
        osocial = ''
        gastos_prom = 0
        honors_prom = 0
        # total_h_paciente = 0
        # total_g_paciente = 0


        for est in pacientes:

            servicios = self.env['puntoingreso.service'].search([('id', 'in', docids), ('patient_ids', '=', est.id)], order="patient_ids")
            _logger.info('servicios_2do')
            _logger.info(servicios)

            ptg = 0
            pth = 0
            paciente = servicios[0].patient_ids.name

            _logger.info('paciente')
            _logger.info(paciente)
            _logger.info('cambia')

            for serv in servicios:

                p_g = self.env['puntoingreso.service'].search([('id', 'in', docids), ('patient_ids', '=', serv.patient_ids.id)])

                _logger.info('p_g_estudios_tildados_paciente')
                _logger.info(p_g)

                for p in p_g:
                    ptg = ptg + p.costos
                    # _logger.info(ptg)
                    pth = pth + p.galeno
                    # _logger.info(pth)

                # total_g_paciente = ptg
                # total_h_paciente = pth
                # _logger.info('total_g_paciente')
                # _logger.info(total_g_paciente)
                # _logger.info('total_h_paciente')
                # _logger.info(total_h_paciente)



                if serv.variant_id.inc_subservicio and not serv.modulada:
                    _logger.info('incluye_subservicios')
                    osocial = serv.osocial
                    subservis = self.env['product.product'].search([('parent_id', '=', serv.variant_id.id)])
                    _logger.info(subservis)

                    for ss in subservis:

                        date_nueva = serv.input_date
                        date_nueva = date_nueva.split('-')
                        date_final = "%s/%s/%s" % (date_nueva[2], date_nueva[1], date_nueva[0])

                        ss_final = dict({
                            'center': serv._get_string_from_selection(),
                            'codigo_servicio': '-',
                            'doctor_ids': serv.doctor_ids,
                            'patient_ids': serv.patient_ids,
                            'n_afiliado': serv.n_afiliado,
                            'input_date': date_final,
                            'variant_id': 0,
                            'service_id': 0,
                            'costos': 0,
                            'galeno': 0,
                            'tarifa': 0,
                            'total_g': 0,
                            'total_h': 0,
                            'total_t': 0
                            })

                        # traemos logica de estudios.py
                        lista_precio_obrasocial = self.env['res.partner'].search([('name', '=', osocial.name),('x_is_osocial','=', True)]).property_product_pricelist.id

                        n_tarifa = None

                        tarifa_estudio = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id)])

                        agregar = True

                        if tarifa_estudio:
                            for x in tarifa_estudio:
                                if (x.date_start != False and x.date_end != False and x.date_start <= serv.input_date and x.date_end >= serv.input_date) or (x.date_end != False and x.date_end >= serv.input_date and x.date_start == False) or (x.date_start != False and x.date_start <= serv.input_date and x.date_end == False) or (x.date_start == False and x.date_end == False):

                                    n_tarifa = x.id
                                    fecha_inicio = x.date_start
                                    fecha_fin = x.date_end
                                    honor = x.min_quantity
                                    costo = x.costo

                        if n_tarifa is None:
                            fecha_inicio = None
                            fecha_fin = None
                            honor = 0
                            costo = 0

                            #costos
                            ss_final['costos'] = 0
                            ss_final['galeno'] = 0
                            ss_final['tarifa'] = 0
                            agregar = False

                        else:
                            fecha_inicio = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).date_start


                            fecha_fin = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).date_end


                            honor = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).min_quantity

                            costo = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).costo

                            t_modulada = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).modulada

                            codigo_servicio = self.env['product.pricelist.item'].search([('pricelist_id', '=', lista_precio_obrasocial),('product_id', '=', ss.id),('id','=',n_tarifa)]).codigo_servicio

                            _logger.info('codigo_sservicio')
                            _logger.info(codigo_servicio)

                            ss_final['codigo_servicio'] = codigo_servicio

                            if t_modulada:

                                tarifa_total = costo
                                costo_total = costo
                                honor_total = 0

                                #costos
                                ss_final['costos'] = costo_total
                                ss_final['galeno'] = honor_total
                                ss_final['tarifa'] = tarifa_total

                            else:
                                #sino todo como estaba
                                multi_costo = self.env['product.template'].browse(ss.product_tmpl_id.id).multi_costo
                                multi_honor = self.env['product.template'].browse(ss.product_tmpl_id.id).multi_honor

                                costo_total = multi_costo * costo
                                honor_total = multi_honor * honor

                                tarifa_total =  costo_total + honor_total

                                #costos
                                ss_final['costos'] = costo_total
                                ss_final['galeno'] = honor_total
                                ss_final['tarifa'] = tarifa_total


                        #datos generales
                        ss_final['service_id'] = ss.product_tmpl_id
                        ss_final['variant_id'] = ss

                        # ss_final['total_g'] = costo_total
                        # ss_final['total_h'] = honor_total
                        # ss_final['total_t'] = tarifa_total

                        _logger.info('ss_final')
                        _logger.info(ss_final)


                        gastos.append(ss_final['costos'])
                        honors.append(ss_final['galeno'])

                        if agregar:
                            estudio_paciente.append(ss_final)

                            resu_add = [ss_final['codigo_servicio'],ss_final['variant_id'].name,1,ss_final['tarifa']]

                            if resu_add not in resumen:
                                resumen.append(resu_add)
                            else:
                                for re in resumen:
                                    if re == resu_add:
                                        re[2] += 1


                        if date_final not in fechas:
                            fechas.append(date_final)


                else:
                    _logger.info('NO_incluye_subservicios')

                    date_nueva = serv.input_date
                    date_nueva = date_nueva.split('-')
                    date_final = "%s/%s/%s" % (date_nueva[2], date_nueva[1], date_nueva[0])

                    serv.total_g = ptg
                    serv.total_h = pth
                    serv.total_t = pth + ptg
                    _logger.info(ptg)
                    _logger.info(pth)
                    _logger.info(pth + ptg)

                    gastos.append(serv.costos)
                    honors.append(serv.galeno)
                    tarifa = serv.tarifa
                    osocial = serv.osocial

                    gastos_prom = gastos_prom+serv.costos
                    honors_prom = honors_prom+serv.galeno

                    _logger.info('mismo')
                    _logger.info(serv)
                    _logger.info(serv.service_id.display_name)

                    ss_final = dict({
                        'center': serv._get_string_from_selection(),
                        'codigo_servicio': serv.codigo_servicio,
                        'doctor_ids': serv.doctor_ids,
                        'patient_ids': serv.patient_ids,
                        'n_afiliado': serv.n_afiliado,
                        'variant_id': serv.variant_id,
                        'service_id': serv.service_id,
                        'input_date': date_final,
                        'costos': serv.costos,
                        'galeno': serv.galeno,
                        'tarifa': serv.tarifa,
                        'total_g': ptg,
                        'total_h': pth,
                        'total_t': (pth + ptg)
                        })

                    #estudio_paciente.append(serv)
                    resu_add = [ss_final['codigo_servicio'],ss_final['variant_id'].name,1,ss_final['tarifa']]
                    if resu_add not in resumen:
                        resumen.append(resu_add)
                    else:
                        for re in resumen:
                            if re == resu_add:
                                re[2] += 1


                    estudio_paciente.append(ss_final)
                    if date_final not in fechas:
                            fechas.append(date_final)

            #estudio_paciente.append(servicios)
            #estudio_paciente.append(serv)

        _logger.info('estudios_paciente')
        _logger.info(estudio_paciente)


        total_total = gastos_prom + honors_prom

        if total_total != 0:
            gastos_por = (gastos_prom * 100) / total_total
            honors_por = (honors_prom * 100) / total_total
        else:
            gastos_por = 0
            honors_por = 0

        #Redondeo a 2 decimales de porcentaje
        gastos_por = math.ceil(gastos_por*100)/100
        honors_por = math.ceil(honors_por*100)/100



        gastos_prom = gastos_prom / len(gastos)
        honors_prom = honors_prom / len(honors)

        #Redondeo a 2 decimales de promedio
        # gastos_prom = math.ceil(gastos_prom*100)/100
        # honors_prom = math.ceil(honors_prom*100)/100
        gastos_prom = round(gastos_prom,2)
        honors_prom = round(honors_prom,2)


        docargs = {
            'fechas': fechas,
            'doc_model': report.model,
            'docs_p': estudio_paciente,
            'osocial': osocial.display_name,
            'resumen': resumen,
            #'docs': pacientes,
            #'doc_ids': docids,
            #'gastos_prom': gastos_prom,
            #'honors_prom': honors_prom,
            #'gastos_por': gastos_por,
            #'honors_por': honors_por,
        }
        return report_obj.render('puntoingreso.report_estudios_data', docargs)

