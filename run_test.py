from app import app, views
#from ini_conf import MyIni

if __name__ == '__main__':
##    my_ini = MyIni('my_ini.conf')
##    s_ini = my_ini.get_sys()
##    h_ini = my_ini.get_hzhbc()
    app.run(port=8098, threaded=True)
