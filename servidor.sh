#!/bin/bash
#
if ! test "$2"; then
  if ! test "$1"; then
    python manage.py runserver
  else
    python manage.py runserver $1:8000
  fi
else
    python manage.py runserver $1:$2
fi

