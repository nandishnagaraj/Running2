workers = 3
bind = 'unix:/run/gunicorn.sock'
chdir = '/home/nandish_nagaraj/Running2/env/bin/'
module = 'greatkart.wsgi:application'
