v = [0.9171337485313416, -0.021161627024412155, 0.0013656718656420708, 0.39801502227783203]

import ujson, time, json
t0 = time.time()
for i in range(1000):
    json.dumps(v)
t1 = time.time()
for i in range(1000):
    ujson.dumps(v)
t2 = time.time()
print('time', t1-t0, t2-t1, (t1-t0)/(t2-t1))

