#!/usr/bin/env python3
#
#  IRIS Source Code
#  Copyright (C) 2021 - Airbus CyberSecurity (SAS)
#  ir@cyberactionlab.net
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

import datetime
from flask_login import current_user
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import joinedload

import logging as log
from app import db
from app.datamgmt.states import update_qualif_state
from app.iris_engine.module_handler.module_handler import call_modules_hook
from app.models import AnalysisStatus
from app.models import AssetComments
from app.models import AssetsType
from app.models import CaseAssets
from app.models import CaseEventsAssets
from app.models import Cases
from app.models import Comments
from app.models import CompromiseStatus
from app.models import Ioc
from app.models import IocAssetLink
from app.models import IocLink
from app.models import IocType
from app.models import CaseQualifDetails
from app.models.authorization import User

def create_qualif(caseid):
    qualif = CaseQualifDetails()
    qualif.qualifinfo = "{}"
    qualif.caseid = caseid

    db.session.add(qualif)
    update_qualif_state(caseid=caseid)
    db.session.commit()

    return qualif

def update_qualif(data, caseid):
    qualif = get_qualif(caseid)
    if (not qualif):
        qualif = create_qualif(caseid)

    qualif.qualifinfo = str(data["qualifinfo"])
    qualif.checklist_info = str(data["checklist_info"])
    update_qualif_state(caseid)

    db.session.commit()


def get_qualif(caseid):
    qualif = CaseQualifDetails.query.filter(
        CaseQualifDetails.caseid == caseid,
    ).first()

    if(not qualif):
        qualif = create_qualif(caseid)

    return qualif