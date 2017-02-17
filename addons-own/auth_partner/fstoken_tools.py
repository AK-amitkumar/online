# -*- coding: utf-8 -*-

from openerp import fields
from openerp.http import request
from openerp.tools.translate import _
import datetime
import time
# from openerp.addons.web.controllers.main import login_and_redirect, set_cookie_and_redirect


def _delay_token_check(wrong_tries=6, delay=3, reset_time=1):

    # First time a wrong token was given for this session
    if not request.session.get('wrong_fstoken_date'):
        request.session['wrong_fstoken_date'] = datetime.datetime.now()
        request.session['wrong_fstoken_tries'] = 1

    # Subsequent wrong token given for this session
    else:
        # Reset if last incorrect try is older than 1h
        if datetime.datetime.now() > request.session['wrong_fstoken_date'] + datetime.timedelta(hours=reset_time):
            request.session.pop('wrong_fstoken_date', False)
            request.session.pop('wrong_fstoken_tries', False)
        else:
            # SECURITY: Add a delay (Todo: Maybe we should close the connection?)
            if request.session['wrong_fstoken_tries'] > wrong_tries:
                time.sleep(delay)
            request.session['wrong_fstoken_tries'] += 1


def fstoken_sanitize(fs_ptoken):
    token = fs_ptoken
    errors = list()

    if not isinstance(token, basestring):
        errors.append(_('Your code is no string!'))
        _delay_token_check()
        return False, errors

    # Remove non alphanumeric characters
    token = ''.join(c for c in token.strip() if c.isalnum())

    # Check minimum token length
    if len(token) < 6:
        errors.append(_('Your code is too short!'))
        _delay_token_check()
        return False, errors

    # Return sanitized token-string and the empty error-messages-list
    return token, errors


def fstoken_check(fs_ptoken):
    # Sanitize token
    token_record, errors = fstoken_sanitize(fs_ptoken)
    if errors:
        # Return empty token and some error message
        return False, False, errors

    # Check if the token record exists and is still valid
    token_record = request.env['res.partner.fstoken'].sudo().search([
        ('name', '=', token_record),
        ('expiration_date', '>=', fields.datetime.now())
    ])
    if not token_record:
        errors.append(_('Wrong or expired code!'))
        _delay_token_check()
        return False, False, errors

    # Check if the token has a res.partner assigned
    partner = token_record.partner_id
    if not partner:
        errors.append(_('The code has no partner assigned!'))
        return False, False, errors

    # Check/Create the res.user for the token
    user = token_record.partner_id.user_ids[0] if token_record.partner_id.user_ids else None
    if not user:
        user = request.env['res.users'].sudo().create({
            'name': partner.name,
            'partner_id': partner.id,
            'email': partner.email,
            'login': partner.email or str(partner.id),
        })
        # Directly commit changes to db in case of login right after this helper function
        request.cr.commit()
    if not user:
        errors.append(_('The code has no user assigned!'))
        return False, False, errors

    # Return fstoken record and the empty error-messages-list
    # ATTENTION: We pass the user on in case it was just created now and
    return token_record, user, errors


# def fstoken_login(fs_ptoken):
#     # Get the token record
#     token_record, user_record, errors = fstoken_check(fs_ptoken)
#     if errors:
#         return False, errors
#
#     # Login the fstoken related res.user
#     user = user_record
#     if request.uid != user.id:
#         # Login
#         # openerp/addons/base/res/res_users.py > authenticate
#         # openerp/addons/web/controllers/main.py > login_and_redirect
#         #uid = request.env['res.users'].authenticate(request.db, user.login, token_record.name)
#         request.cr.commit()
#         uid = request.session.authenticate(request.db, password=token_record.name, uid=user.id)
#         request.cr.commit()
#         # Check uid after login
#         if request.uid != uid:
#             errors.append(_('Login by fstoken failed!'))
#             return False, errors
#
#     # Return fstoken record and the empty error-messages-list
#     return token_record, errors
