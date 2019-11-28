# -*- coding: utf-8 -*-
import json
import time
import uuid

import arrow
from flask import g, request, make_response, jsonify, abort

from . import db, app, cache, logger, access_logger, msg_logger
from .models import *
from . import helper


@app.route('/')
def index_get():
    result = {
        'vehicle_pass': '%svehicle_pass' % (request.url_root)
    }
    header = {'Cache-Control': 'public, max-age=60'}
    return jsonify(result), 200, header


@app.route('/vehicle_pass', methods=['POST'])
def vehicle_pass_post():
    if not request.json:
        return jsonify({'message': 'Problems parsing JSON'}), 415
    try:
        uu_id = str(uuid.uuid4())
        plate_no = request.json['AlarmInfoPlate']['result']['PlateResult']['license']
        plate_color = request.json['AlarmInfoPlate']['result']['PlateResult']['colorType']
        pass_time = arrow.get(request.json['AlarmInfoPlate']['result']['PlateResult']['timeStamp']['Timeval']['sec']).to('Asia/Shanghai')
        ip_addr = request.json['AlarmInfoPlate']['ipaddr']
        device_name = request.json['AlarmInfoPlate']['deviceName']
        serialno = request.json['AlarmInfoPlate']['serialno']
        path_seq = (app.config['BASE_PATH'], 'Plate', pass_time.format('YYYYMMDD'), serialno, pass_time.format('HH'))
        img_path = '/'.join(path_seq)
        name = '{0}_{1}_{2}'.format(pass_time.format('YYYYMMDDHHmmss'), serialno, helper.ip2int(ip_addr))
        pic_path1 = request.json['AlarmInfoPlate']['result']['PlateResult']['imageFile']
        pic_path2 = request.json['AlarmInfoPlate']['result']['PlateResult']['imageFragmentFile']
        pic_url1 = pic_path1.replace(app.config['BASE_PATH'], app.config['BASE_URL_PATH'])
        pic_url2 = pic_path2.replace(app.config['BASE_PATH'], app.config['BASE_URL_PATH'])
        
        vehicle = VehiclePass(plate_no=plate_no, plate_color=plate_color,
                       pass_time=pass_time.datetime, site_id='1',
                       pic1=pic_url1, pic2=pic_url2, ip_addr=ip_addr,
                       device_name=device_name, uuid=uu_id)
        db.session.add(vehicle)
        db.session.commit()
        msg_logger.info(request.json)
    except Exception as e:
        logger.error(e)
        raise
    return jsonify({}), 201

