#   Copyright (C) 2020 Sean D'Epagnier
#
# This Program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.  

# read and parse custom hat file describing tinypilot gpio periphials before
# python is fully loaded using micropython

import ujson
lcd = 'nokia5110' # by default if no hat file
try:
    f=open('/sys/firmware/devicetree/base/hat/custom_0')
    x=f.read()
    data=ujson.loads(x)

    lcd = data['lcd']['driver']
except Exception as e:
    print('except', e)
    
print('lcd', lcd)
f=open('/home/tc/.pypilot/lcddriver', 'w')
f.write(lcd)
f.close()
