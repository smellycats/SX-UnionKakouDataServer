# -*- coding: utf-8 -*-
import arrow

from app import db
from app.models import Users, Scope, Traffic
from app.helper import *


def test_scope_get():
    scope = Scope.query.all()
    for i in scope:
        print i.name

def test_user_get():
    user = Users.query.filter_by(username='admin', banned=0).first()
    print user.scope
    
def test_traffic_get():
    r = Traffic.query.first()
    #help(r)
    print type(r.pass_time)
    #print r.crossing_id

def test_traffic_add():
    t_list = []
    for i in range(3):
        t = Traffic(crossing_id='441302123', lane_no=1, direction_index='IN',
                    plate_no=u'粤L12345', plate_type='',
                    pass_time='2015-12-13 01:23:45', plate_color='0')
        db.session.add(t)
        t_list.append(t)
    db.session.commit()
    r = [{'pass_id': r.pass_id} for r in t_list]
    print r


if __name__ == '__main__':
    #hpys_test()
    #hbc_add()
    #test_scope_get()
    #test_user_get()
    #test_hbc_get()
    #test_hbc_add()
    #test_hbcimg_get()
    #test_kkdd()
    test_traffic_get()
    test_traffic_add()


