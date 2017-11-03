# -*- coding: utf-8 -*-
import json
from functools import wraps

import arrow
from flask import g, request, make_response, jsonify, abort
from flask_restful import reqparse, abort, Resource
from passlib.hash import sha256_crypt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import db, app, auth, limiter, cache, logger, access_logger
from models import *
#from help_func import *
import helper


def verify_addr(f):
    """IP地址白名单"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not app.config['WHITE_LIST_OPEN'] or \
           request.remote_addr in set(['127.0.0.1', 'localhost']) or \
           request.remote_addr in app.config['WHITE_LIST']:
            pass
        else:
            return jsonify({
                'status': '403.6',
                'message': u'123'}), 403
        return f(*args, **kwargs)
    return decorated_function


@auth.verify_password
@cache.memoize(60 * 5)
def verify_pw(username, password):
    user = Users.query.filter_by(username=username).first()
    if user:
        g.uid = user.id
        g.scope = set(user.scope.split(','))
        return sha256_crypt.verify(password, user.password)
    return False


def verify_scope(scope):
    def scope(f):
        """权限范围验证装饰器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'all' in g.scope or scope in g.scope:
                return f(*args, **kwargs)
            else:
                abort(405)
        return decorated_function
    return scope


@app.route('/')
@limiter.limit("5000/hour")
#@auth.login_required
def index_get():
    result = {
        'user_url': 'http://%suser{/user_id}' % (request.url_root),
        'scope_url': 'http://%sscope' % (request.url_root),
        # 'token_url': 'http://%stoken' % (request.url_root),
        'kakou_url': 'http://%skakou/' % (request.url_root)
    }
    header = {'Cache-Control': 'public, max-age=60, s-maxage=60'}
    return jsonify(result), 200, header
    

@app.route('/user', methods=['OPTIONS'])
@limiter.limit('5000/hour')
def user_options():
    return jsonify(), 200

@app.route('/user/<int:user_id>', methods=['GET'])
@limiter.limit('5000/hour')
@auth.login_required
def user_get(user_id):
    user = Users.query.filter_by(id=user_id, banned=0).first()
    if user:
        result = {
            'id': user.id,
            'username': user.username,
            'scope': user.scope,
            'date_created': str(user.date_created),
            'date_modified': str(user.date_modified),
            'banned': user.banned
        }
        return jsonify(result), 200
    else:
        abort(404)

@app.route('/user/<int:user_id>', methods=['POST', 'PATCH'])
@limiter.limit('5000/hour')
@auth.login_required
def user_patch(user_id):
    if not request.json:
        return jsonify({'message': 'Problems parsing JSON'}), 415
    if not request.json.get('scope', None):
        error = {
            'resource': 'user',
            'field': 'scope',
            'code': 'missing_field'
        }
        return jsonify({'message': 'Validation Failed', 'errors': error}), 422
    # 所有权限范围
    all_scope = set()
    for i in Scope.query.all():
        all_scope.add(i.name)
    # 授予的权限范围
    request_scope = set(request.json.get('scope', u'null').split(','))
    # 求交集后的权限
    u_scope = ','.join(all_scope & request_scope)

    db.session.query(Users).filter_by(id=user_id).update(
        {'scope': u_scope, 'date_modified': arrow.now().datetime})
    db.session.commit()

    user = Users.query.filter_by(id=user_id).first()

    return jsonify({
        'id': user.id,
        'username': user.username,
        'scope': user.scope,
        'date_created': str(user.date_created),
        'date_modified': str(user.date_modified),
        'banned': user.banned
    }), 201

@app.route('/user', methods=['POST'])
@limiter.limit('5000/hour')
@auth.login_required
def user_post():
    if not request.json:
        return jsonify({'message': 'Problems parsing JSON'}), 415
    if not request.json.get('username', None):
        error = {
            'resource': 'user',
            'field': 'username',
            'code': 'missing_field'
        }
        return jsonify({'message': 'Validation Failed', 'errors': error}), 422
    if not request.json.get('password', None):
        error = {
            'resource': 'user',
            'field': 'password',
            'code': 'missing_field'
        }
        return jsonify({'message': 'Validation Failed', 'errors': error}), 422
    if not request.json.get('scope', None):
        error = {
            'resource': 'user',
            'field': 'scope',
            'code': 'missing_field'
        }
        return jsonify({'message': 'Validation Failed', 'errors': error}), 422
    
    user = Users.query.filter_by(username=request.json['username'],
                                 banned=0).first()
    if user:
        return jsonify({'message': 'username is already esist'}), 422

    password_hash = sha256_crypt.encrypt(
        request.json['password'], rounds=app.config['ROUNDS'])
    # 所有权限范围
    all_scope = set()
    for i in Scope.query.all():
        all_scope.add(i.name)
    # 授予的权限范围
    request_scope = set(request.json.get('scope', u'null').split(','))
    # 求交集后的权限
    u_scope = ','.join(all_scope & request_scope)
    u = Users(username=request.json['username'], password=password_hash,
              scope=u_scope, banned=0)
    db.session.add(u)
    db.session.commit()
    result = {
        'id': u.id,
        'username': u.username,
        'scope': u.scope,
        'date_created': str(u.date_created),
        'date_modified': str(u.date_modified),
        'banned': u.banned
    }
    return jsonify(result), 201

@app.route('/scope', methods=['OPTIONS'])
@limiter.limit('5000/hour')
def scope_options():
    return jsonify(), 200

@app.route('/scope', methods=['GET'])
@limiter.limit('5000/hour')
def scope_get():
    items = map(helper.row2dict, Scope.query.all())
    return jsonify({'total_count': len(items), 'items': items}), 200


@cache.memoize(60)
def get_bk_by_hphm(hphm):
    return TrafficDispositionVehicle.query.filter_by(plate_no=hphm, del_flag=0).first()

# 添加布控车牌
def set_bkcp(i):
    if i['hphm'] == '-' or i['hphm'] is None:
	return
    tsv = get_bk_by_hphm(i['hphm'])
    if tsv is None:
	return

    fxbh = {u'IN': 9, u'OT': 10, u'WE': 2, u'EW': 1,u'SN': 3, u'NS':4}
    hpzl = helper.hphm2hpzl(i['hphm'], i['hpys_id'], i['hpzl'])
    sql = (u"insert into traffic_disposition_alarm(disposition_type, disposition_id, disposition_reason, crossing_id, lane_no, direction_index, pass_time, plate_no, plate_type, plate_color, vehicle_speed, image_path) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}')".format(tsv.disposition_type, tsv.disposition_id, tsv.disposition_reason, i['kkdd_id'], i['cdbh'], fxbh.get(i['fxbh'], 9), i['jgsj'], i['hphm'], hpzl, i['hpys_id'], i['clsd'], i['img_path']))
    query = db.get_engine(app, bind='kakou').execute(sql)
    query.close()

@cache.memoize(60)
def get_special_vehicle():
    try:
        r = set()
        t = TrafficSpecialVehicle.query.filter_by().all()
        for i in t:
	    r.add((i.plate_no, int(i.plate_color)))
        return r
    except Exception as e:
	logger.exception(e)
	return set()

# 判断是否白名单车辆
def is_spcp(i):
    if i['hphm'] == '-' or i['hphm'] is None:
	return False
    sp = get_special_vehicle()
    if (i['hphm'], i['hpys_id']) in sp:
	return True
    return False

@app.route('/kakou', methods=['POST'])
#@limiter.limit('5000/hour')
@limiter.exempt
#@auth.login_required
def kakou_post():
    if not request.json:
        return jsonify({'message': 'Problems parsing JSON'}), 415
    #tra_list = []
    fxbh = {u'IN': 9, u'OT': 10, u'WE': 2, u'EW': 1,u'SN': 3, u'NS':4}
    try:
	# 正常车辆数据
	vals = []
	# 白名单数据
	w_vals = []
	for i in request.json:
	    hpzl = helper.hphm2hpzl(i['hphm'], i['hpys_id'], i['hpzl'])

	    if is_spcp(i):
	    	w_vals.append(u"('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}')".format(
		    i['kkdd_id'], i['cdbh'], fxbh.get(i['fxbh'], 9), i['hphm'], hpzl, i['jgsj'], i['hpys_id'], i['img_path'], 0, 0, i['clsd']))
	    else:
		set_bkcp(i)
	    	vals.append(u"('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}')".format(
		    i['kkdd_id'], i['cdbh'], fxbh.get(i['fxbh'], 9), i['hphm'], hpzl, i['jgsj'], i['hpys_id'], i['img_path'], 0, 0, i['clsd']))
	if len(vals) > 0:
	    sql = (u"insert into traffic_vehicle_pass(crossing_id, lane_no, direction_index, plate_no, plate_type, pass_time, plate_color, image_path, vehicle_color, vehicle_type, vehicle_speed) VALUES %s" % ','.join(vals))
	    query = db.get_engine(app, bind='kakou').execute(sql)
	    query.close()
	if len(w_vals) > 0:
	    try:
	        sql2 = (u"insert into traffic_privilegevehicle_pass(crossing_id, lane_no, direction_index, plate_no, plate_type, pass_time, plate_color, image_path, vehicle_color, vehicle_type, vehicle_speed) VALUES %s" % ','.join(w_vals))
	        query = db.get_engine(app, bind='kakou').execute(sql2)
		query.close()
	    except Exception as e:
		pass
		#logger.exception(e)
    except Exception as e:
	logger.error('request.json')
	logger.error(request.json)
        logger.exception(e)
        raise
    
    return jsonify({'total': len(request.json)}), 201

