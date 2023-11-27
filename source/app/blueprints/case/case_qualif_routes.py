#!/usr/bin/env python3
#
#  IRIS Source Code
#  Copyright (C) 2021 - Airbus CyberSecurity (SAS) - DFIR-IRIS Team
#  ir@cyberactionlab.net - contact@dfir-iris.org
#
#  Custom module for CERT Santé - Made by Olivier Ruet-Cros
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# IMPORTS ------------------------------------------------
from datetime import datetime

import csv
import ast
import marshmallow
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_wtf import FlaskForm

import logging as log
import json
from app import db
from app.blueprints.case.case_comments import case_comment_update
from app.datamgmt.case.case_db import get_case
from app.datamgmt.case.case_db import get_case_client_id
from app.datamgmt.case.case_iocs_db import get_iocs
from app.datamgmt.case.case_qualif_db import update_qualif
from app.datamgmt.case.case_qualif_db import get_qualif
from app.datamgmt.case.case_qualif_db import create_qualif
from app.datamgmt.manage.manage_attribute_db import get_default_custom_attributes
from app.datamgmt.manage.manage_users_db import get_user_cases_fast
from app.iris_engine.module_handler.module_handler import call_modules_hook
from app.iris_engine.utils.tracker import track_activity
from app.forms import ModalAddCaseAssetForm
from app.models import AnalysisStatus
from app.models import Ioc
from app.models import IocAssetLink
from app.models import IocLink
from app.models.authorization import CaseAccessLevel
from app.schema.marshables import CommentSchema
from app.util import ac_api_case_requires
from app.util import ac_case_requires
from app.util import response_error
from app.util import response_success


case_qualif_blueprint = Blueprint('case_qualif',
                                  __name__,
                                  template_folder='templates')

@case_qualif_blueprint.route('/case/qualif', methods=['GET'])
@ac_case_requires(CaseAccessLevel.read_only, CaseAccessLevel.full_access)
def case_archi(caseid, url_redir):
    """
    Returns the page of case qualif, with all the details about the target architectures.
    :return: The HTML page of case architecture
    """
    if url_redir:
        return redirect(url_for('case_qualif.case_qualif', cid=caseid, redirect=True))

    form = ModalAddCaseAssetForm()

    # Retrieve the assets linked to the investigation
    case = get_case(caseid)

    return render_template("case_qualif.html", case=case, form=form)

@case_qualif_blueprint.route('/case/qualif/get', methods=['POST'])
@ac_case_requires(CaseAccessLevel.read_only, CaseAccessLevel.full_access)
def case_archi_get(caseid, url_redir):
    qualif = get_qualif(caseid)
    if(qualif == None):
        qualif = create_qualif(caseid)
    form_data = {}
    if(qualif.qualifinfo == None):
        qualif.qualifinfo = ""
    if(qualif.checklist_info == None):
        qualif.checklist_info = "{}"
    form_data["qualifinfo"] = ast.literal_eval(qualif.qualifinfo)
    form_data["checklist_info"] = ast.literal_eval(qualif.checklist_info)

    return response_success(msg="OK", data=form_data)

@case_qualif_blueprint.route('/case/qualif/refresh', methods=['POST'])
@ac_case_requires(CaseAccessLevel.read_only, CaseAccessLevel.full_access)
def case_qualif_refresh(caseid, url_redir):
    """
    Saves and reload current qualif info
    """
    jsdata = request.get_json()
    update_qualif(jsdata, caseid)

    qualif = get_qualif(caseid)
    if(qualif == None):
        qualif = create_qualif(caseid)
    form_data = ast.literal_eval(qualif.qualifinfo)

    return response_success(msg="OK", data=form_data)

@case_qualif_blueprint.route('/case/qualif/save', methods=['POST'])
@ac_case_requires(CaseAccessLevel.read_only, CaseAccessLevel.full_access)
def case_qualif_save(caseid, url_redir):
    """
    Saves current qualification info
    """
    jsdata = request.get_json()
    update_qualif(jsdata, caseid)

    return response_success(msg="OK", data="")

@case_qualif_blueprint.route('/case/qualif/export', methods=['POST'])
@ac_case_requires(CaseAccessLevel.read_only, CaseAccessLevel.full_access)
def case_qualif_export(caseid, url_redir):
    """
    Exports current qualification info to JSON file
    """
    jsdata = request.get_json()

    return response_success(msg="OK", data="")