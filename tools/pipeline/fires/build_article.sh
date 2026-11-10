#!/bin/sh
# Rebuild site/kuwait-oil-fires.html from article_src.html + the generated Kuwait map.
cd "$(dirname "$0")" && python3 article_map.py > /tmp/fires_map.svg && python3 -c "
s=open('article_src.html',encoding='utf-8').read(); m=open('/tmp/fires_map.svg',encoding='utf-8').read()
open('../../../site/kuwait-oil-fires.html','w',encoding='utf-8').write(s.replace('__MAP__',m))"
