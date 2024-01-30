# -*- coding: utf-8 -*-

import datetime, ftputil, logging
from odoo import models, fields, api
import base64
import json
try:
    import ftputil.session
except ImportError:
    pass
# import ftplib

_logger = logging.getLogger(__name__)


class FTPConfig(models.Model):
    _name = 'ftp.config'
    _description = 'Connection info of FTP Transfers'


    server = fields.Char(string='Server', help="Servername, including protocol, e.g. https://prod.barneveldsekrant.nl")
    directory = fields.Char(string='Server subdir', help="Directory starting with slash, e.g. /api/v1, or empty")
    tempdir = fields.Char(string='Local temp dir', help="Local temporary directory. e.g. /home/odoo")
    ftp = fields.Boolean(string='Use FTP', help="Enable when using FTP")
    sftp = fields.Boolean(string='Use SFTP', help="Enable when using SFTP instead of FTP")
    port = fields.Char(string='Port', help="For ftp use port 21, for SFT use port 22")
    user = fields.Char(string='User')
    password = fields.Char(string='Password')

    latest_run = fields.Char(string='Latest run', help="Date of latest run of Announcement connector", copy=False)
    latest_status = fields.Char(string='Latest status', help="Log of latest run", copy=False)
    output_type = fields.Selection([('csv','CSV'), ('xml', 'XML'), ('json','JSON')], string='Output File Format', default='csv')

    active = fields.Boolean(string='Active', default=True)
    description = fields.Char(string='Description')

    sql_export_ids = fields.Many2many('sql.export', 'sql_export_ftp_rel', 'lead_id', 'sql_export_id',
                                      string='SQL Exports')


    
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

        if self.sftp:
            port_int = int(config.port)
            # Initiate SFTP File Transfer Connection
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=config.server, port=port_int, username=config.user, password=config.password, look_for_keys=False)
                sftp = ssh.open_sftp()
            except Exception, e:
                self.log_exception(msg, "Invalid FTPs configuration/credentials")
                return False
            try:
                _logger.info("Transferring " + filename)
                if config.directory:
                    target = str(config.directory)
                else:
                    target = '/'
                source = config.tempdir + '/'
                sftp.put(source + filename, target + filename)
                sftp.close()
                ssh.close()
            except Exception, e:
                config.log_exception(msg, "Transfer failed, quiting....%s" % (e))
                sftp.close()
                ssh.close()

                return False

        elif self.ftp:
            # Initiate FTP File Transfer Connection
            try:
                # ftpServer = ftplib.FTP(config.server, config.user, config.password)
                # ftpServer.encoding = "utf-8"
                port_session_factory = ftputil.session.session_factory(port=config.port, use_passive_mode=True)
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
                ftpServer.close()

            except Exception, e:
                config.log_exception(msg, "Transfer failed, quiting....%s" % (e))
                ftpServer.close()

                return False

        return True
    
    def automated_run(self):
        configurations = self.search([])
        for config in configurations:
            try:
                config.do_send()
            except Exception, e:
                pass

    
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
                        filename = str(se.name) + '.xml'
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
                        filename = str(se.name) + '.json'
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


    
    def export_sql(self, sqlExport):
        self.ensure_one()
        wiz = self.env['sql.file.wizard'].create({
            'sql_export_id': sqlExport.id})
        sql_export = sqlExport

        # Manage Params
        variable_dict = {}

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
            'file_name': sql_export.name + '.csv'
        })
        return wiz
