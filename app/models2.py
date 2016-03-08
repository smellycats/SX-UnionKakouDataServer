# -*- coding: utf-8 -*-
import arrow

from . import db


class Users(db.Model):
    """用户"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True)
    password = db.Column(db.String(128))
    scope = db.Column(db.String(128), default='')
    date_created = db.Column(db.DateTime, default=arrow.now().datetime)
    date_modified = db.Column(db.DateTime, default=arrow.now().datetime)
    banned = db.Column(db.Integer, default=0)

    def __init__(self, username, password, scope='', banned=0,
                 date_created=None, date_modified=None):
        self.username = username
        self.password = password
        self.scope = scope
        now = arrow.now().datetime
        if not date_created:
            self.date_created = now
        if not date_modified:
            self.date_modified = now
        self.banned = banned

    def __repr__(self):
        return '<Users %r>' % self.id


class Scope(db.Model):
    """权限范围"""
    __tablename__ = 'scope'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Scope %r>' % self.id


class Traffic(db.Model):
    """过车信息"""
    __bind_key__ = 'kakou'
    __tablename__ = 'traffic_vehicle_pass'
    pass_id = db.Column(db.Integer, primary_key=True)
    crossing_id = db.Column(db.Integer, default=0)
    lane_no = db.Column(db.Integer, default=1)
    direction_index = db.Column(db.Integer, default=0)
    plate_no = db.Column(db.String(20), default='-')
    plate_type = db.Column(db.String(10), default='')
    pass_time = db.Column(db.DateTime, default=0)
    vehicle_speed = db.Column(db.Integer, default=0)
    vehicle_len = db.Column(db.Integer, default=0)
    plate_color = db.Column(db.String(10), default='0')
    vehicle_color = db.Column(db.String(10), default='Z')
    vehicle_type = db.Column(db.String(10), default='X99')
    vehicle_color_depth = db.Column(db.String(10), default='')
    plate_state = db.Column(db.String(10), default='0')
    image_path = db.Column(db.String(256), default='')
    plate_image_path = db.Column(db.String(256), default='')
    tfs_id = db.Column(db.Integer, default=0)
    vehicle_state = db.Column(db.Integer, default=0)
    vehicle_info_level = db.Column(db.Integer, default=1)
    vehicle_logo = db.Column(db.Integer, default=0)
    vehicle_sublogo = db.Column(db.Integer, default=0)
    vehicle_model = db.Column(db.Integer, default=0)
    pilotsunvisor = db.Column(db.Integer, default=0)
    

    def __init__(self, crossing_id=0, lane_no=1, direction_index=0, plate_no='-',
                 plate_type='', pass_time=0, vehicle_speed=0, vehicle_len=0,
                 plate_color, vehicle_color='Z', vehicle_type='X99',
                 vehicle_color_depth='', plate_state='0', image_path='',
                 plate_image_path='', tfs_id='', vehicle_state=0,
                 vehicle_info_level=1, vehicle_logo=0, vehicle_sublogo=0,
                 vehicle_model=0, pilotsunvisor=0):
        self.crossing_id = crossing_id
        self.lane_no = lane_no
        self.direction_index = direction_index
        self.plate_no = plate_no
        self.plate_type = plate_type
        self.pass_time = pass_time
        self.vehicle_speed = vehicle_speed
        self.vehicle_len = vehicle_len
        self.plate_color = plate_color
        self.vehicle_color = vehicle_color
        self.vehicle_type = vehicle_type
        self.vehicle_color_depth = vehicle_color_depth
        self.plate_state = plate_state
        self.image_path = image_path
        self.plate_image_path = plate_image_path
        self.tfs_id = tfs_id
        self.vehicle_state = vehicle_state
        self.vehicle_info_level = vehicle_info_level
        self.vehicle_logo = vehicle_logo
        self.vehicle_sublogo = vehicle_sublogo
        self.vehicle_model = vehicle_model
        self.pilotsunvisor = pilotsunvisor

    def __repr__(self):
        return '<Traffic %r>' % self.pass_id

