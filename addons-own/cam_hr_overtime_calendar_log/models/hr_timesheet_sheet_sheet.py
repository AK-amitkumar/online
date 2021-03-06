# -*- coding: utf-'8' "-*-"
from openerp import models, api
import logging
_logger = logging.getLogger(__name__)


class HRTimesheetSheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    @api.multi
    def _total_sums(self, field_name=None, arg=None):
        _logger.info("_total_sums(), field_name: %s, arg: %s" % (field_name, arg))
        # Make sure all entries created by calendar events are correct
        cal_obj = self.env['calendar.event']
        for sheet in self:
            # HINT: used start_date twice instead of end_date to catch overday events
            events_to_update = cal_obj.search([('user_id', '=', sheet.user_id.id),
                                               ('start_datetime', '>=', sheet.date_from + ' 00:00:00'),
                                               ('start_datetime', '<=', sheet.date_to + ' 23:59:59'),
                                               ])
            _logger.info("_total_sums() found %s calendar events in this timesheet range" % len(events_to_update))
            for event in events_to_update:
                vals = {}
                if event.is_worklog and not event.project_id:
                    vals['is_worklog'] = False
                event.write(vals)
            _logger.info("_total_sums() all calendar event related work-log and attendance records updated")

        return super(HRTimesheetSheetSheet, self)._total_sums(field_name=field_name, arg=arg)
