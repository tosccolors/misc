# -*- coding: utf-8 -*-

import datetime, ftputil, logging
from odoo import models, fields, api
import base64
import json
try:
    import ftputil.session
except ImportError:
    pass
import ftplib

_logger = logging.getLogger(__name__)


class FTPConfig(models.Model):
    _name = 'ftp.config'
    _description = 'Connection info of FTP Transfers'


    server = fields.Char(string='Server', help="Servername, including protocol, e.g. https://prod.barneveldsekrant.nl")
    directory = fields.Char(string='Server subdir', help="Directory starting with slash, e.g. /api/v1, or empty")
    tempdir = fields.Char(string='Local temp dir', help="Local temporary directory. e.g. /home/odoo")
    user = fields.Char(string='User')
    password = fields.Char(string='Password')

    latest_run = fields.Char(string='Latest run', help="Date of latest run of Announcement connector", copy=False)
    latest_status = fields.Char(string='Latest status', help="Log of latest run", copy=False)
    output_type = fields.Selection([('csv','CSV'), ('xml', 'XML'), ('json','JSON')], string='Output File Format', default='csv')

    active = fields.Boolean(string='Active', default=True)
    description = fields.Char(string='Description')

    sql_export_ids = fields.Many2many('sql.export', 'sql_export_ftp_rel', 'lead_id', 'sql_export_id',
                                      string='SQL Exports')

    # show only first record to configure, no options to create an additional one
    # @api.multi
    # def default_view(self):
    #     configurations = self.search([])
    #     if not configurations:
    #         server = "bdu.nl"
    #         self.write({'server': server})
    #         configuration = self.id
    #         _logger.info("configuration created")
    #     else:
    #         configuration = configurations[0].id
    #     action = {
    #         "type": "ir.actions.act_window",
    #         "res_model": "ftp.config",
    #         "view_type": "form",
    #         "view_mode": "form",
    #         "res_id": configuration,
    #         "target": "inline",
    #     }
    #     return action


    # @api.multi
    # def save_config(self):
    #     self.write({})
    #     return True

    @api.multi
    def name_get(self):
        return [(rec.id, "%s (%s)" % (rec.server, rec.user)) for rec in self]


    def log_exception(self, msg, final_msg, clear=False):
        for config in self:
            _logger.exception(final_msg)
            config.latest_run = datetime.datetime.utcnow().strftime('UTC %Y-%m-%d %H:%M:%S ')
            if clear:
                config.latest_status = msg + final_msg
            else:
                config.latest_status += str('\n ') + msg + final_msg
            # config.write({})
        return

    # def ship_file(self, msg, data, filename):
    #     for config in self:
    #         path = config.tempdir + "/"
    #
    #         # JSON
    #         if isinstance(data, dict):
    #             with open(path + filename, 'a') as f:
    #                 json.dump(data, f)
    #         else:
    #             f = open(path + filename, "w")
    #             f.write(data)
    #
    #         f = None  # to force releasing the file handle
    #
    #         # Initiate File Transfer Connection
    #         try:
    #             port_session_factory = ftputil.session.session_factory(port=21, use_passive_mode=True)
    #             ftp = ftputil.FTPHost(config.server, config.user, config.password, session_factory=port_session_factory)
    #         except Exception, e:
    #             config.log_exception(msg, "Invalid FTP configuration")
    #             continue
    #
    #         try:
    #             _logger.info("Transferring " + filename)
    #             if config.directory:
    #                 target = str(config.directory) + '/' + filename
    #             else:
    #                 target = '/' + filename
    #             source = config.tempdir + '/' + filename
    #             ftp.upload(source, target)
    #         except Exception, e:
    #             config.log_exception(msg, "Transfer failed, quiting....")
    #             continue
    #
    #         ftp.close()
    #
    #     return True

    def ship_file(self, msg, data, filename):
        for config in self:
            path = config.tempdir + "/"

            try:
                # JSON
                if isinstance(data, dict):
                    with open(path + filename, 'a') as f:
                        json.dump(data, f)
                else:
                    f = open(path + filename, "w")
                    f.write(data)
                f = None  # to force releasing the file handle

            except Exception, e:
                config.log_exception(msg, "Invalid Directory, quiting...")
                continue


            # Initiate File Transfer Connection
            try:
                # ftpServer = ftplib.FTP(config.server, config.user, config.password)
                # ftpServer.encoding = "utf-8"
                port_session_factory = ftputil.session.session_factory(port=21, use_passive_mode=True)
                ftpServer = ftputil.FTPHost(config.server, config.user, config.password, session_factory=port_session_factory)

            except Exception, e:
                config.log_exception(msg, "Invalid FTP configuration, quiting...")
                return False

            try:
                _logger.info("Transferring " + filename)
                if config.directory:
                    target = str(config.directory)
                else:
                    target = '/'

                source = config.tempdir + '/'

                # # ===========================
                # ftpServer.cwd(target)
                # with open(source + filename, "rb") as file:
                #     ftpServer.storbinary("STOR %s"%(filename), fp=file)
                # ftpServer.quit()
                # # ============================

                ftpServer.upload(source + filename, target + filename)

            except Exception, e:
                config.log_exception(msg, "Transfer failed, quiting....%s"%(e))
                ftpServer.close()
                return False

            ftpServer.close()

        return True

    # @api.multi
    # def automated_run(self):
    #     configurations = self.search([])
    #     if not configurations:
    #         # cannot use local method because there is no record
    #         _logger.exception("Cannot start automated_run. Need a valid configuration")
    #         return False
    #     else:
    #         # start with previous end
    #         # self = configurations[0]
    #         return self.do_send()

    @api.multi
    def automated_run(self):
        configurations = self.search([])
        _logger.info('Calling RUN found ....> %s '%(configurations.ids))
        for config in configurations:
            try:
                _logger.info('Try Starting on [%s]'%(config.description))
                config.do_send()
            except Exception, e:
                _logger.exception("Cannot start automated_run. %s"%(e))

    @api.multi
    def do_send(self):
        cursor = self._cr
        msg = ""
        for config in self:
            config.log_exception(msg, '', clear=True)
            if not config:
                config.log_exception(msg, "No configuration found. <br>Please configure FTP connector.")
                continue
            elif not config.output_type:
                config.log_exception(msg, "Output Format of the File not defined. <br>Please configure FTP connector.")
                continue
            elif not config.server or not config.user or not config.password or not config.tempdir:
                config.log_exception(msg,
                                   "Program not started. <br>Please provide a valid server/user/password/tempdir configuration")
                continue

            # sqlExports = self.env['sql.export'].search([('state','=', 'sql_valid')], order='id')
            sqlExports = config.sql_export_ids.filtered(lambda s: s.state == 'sql_valid')

            if not len(sqlExports.ids):
                config.log_exception(msg,
                                   "Program not started. <br>Please create a valid record in SQL Export, & ensure it is in 'SQL Valid' state ")
                continue

            GoON = True
            OkFiles = ErrFiles = 0
            for idx, se in enumerate(sqlExports):
                try:
                    if config.output_type == 'xml':
                        query = 'SELECT query_to_xml(\'' + str(se.query) + '\',\
                                                      true,false,\'\')'

                        cursor.execute(query)
                        res = cursor.fetchall()
                        res = res[0][0]
                        filename = str(se.id) + '_' + str(se.name) + '.xml'
                        GoON = config.ship_file(msg, res, filename)
                        if not GoON: return False

                    elif config.output_type == 'csv':
                        wizRec = self.export_sql(sqlExport=se)
                        data = base64.decodestring(wizRec.binary_file)
                        GoON = config.ship_file(msg, data, wizRec.file_name)
                        if not GoON: return False

                    else: # JSON
                        cursor.execute(se.query)
                        res = cursor.dictfetchall()
                        data = {'0': res}
                        filename = str(se.id) + '_' + str(se.name) + '.json'
                        GoON = config.ship_file(msg, data, filename)
                        if not GoON: return False

                    OkFiles += 1

                except Exception, e:
                    ErrFiles += 1
                    config.log_exception(msg, "Error executing SQL (%s) :: %s"%(se.name, e))
                    continue

            # report and exit positively
            final_msg = "File(s) transferred: %s Success & %s Failed out of %s file(s)..."%(OkFiles, ErrFiles, idx+1 )
            config.log_exception(msg, final_msg)
        return True


    # def do_send(self):
    #
    #     for config in self:
    #         print ("Transferring to =====", config.server)
    #         import ftplib
    #         ftp_server = ftplib.FTP(config.server, config.user, config.password)
    #         ftp_server.encoding = "utf-8"
    #         filename = '2_Accounts.xml'
    #         sourcepath = '/home/deep/Downloads/'
    #         destpath = '/odoo'
    #         # with open(sourcepath + filename, "rb") as file:
    #         #     # Command for Uploading the file "STOR filename"
    #         #     ftp_server.storbinary("STOR %s"%(filename), fp=file)
    #
    #         file = open(sourcepath + filename, "rb")
    #         ftp_server.cwd(destpath)
    #         ftp_server.storbinary('STOR ' + filename, file)
    #         ftp_server.quit()
    #         ftp_server.close()



    @api.multi
    def export_sql(self, sqlExport):
        self.ensure_one()
        wiz = self.env['sql.file.wizard'].create({
            'sql_export_id': sqlExport.id})
        sql_export = sqlExport

        # Manage Params
        variable_dict = {}
        # today = datetime.datetime.now()
        # today_tz = fields.Datetime.context_timestamp(
        #     sql_export, today)

        if sql_export.field_ids:
            for field in sql_export.field_ids:
                variable_dict[field.name] = self[field.name]
        if "%(company_id)s" in sql_export.query:
            variable_dict['company_id'] = self.env.user.company_id.id
        if "%(user_id)s" in sql_export.query:
            variable_dict['user_id'] = self._uid

        # Execute Request
        res = sql_export._execute_sql_request(
            params=variable_dict, mode='stdout',
            copy_options=sql_export.copy_options)
        if wiz.sql_export_id.encoding:
            res = res.encode(wiz.sql_export_id.encoding)

        wiz.write({
            'binary_file': res,
            'file_name': str(sql_export.id) + '_' + sql_export.name + '.csv'
        })
        return wiz
