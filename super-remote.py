# Released by rdb under the Unlicense (unlicense.org)
# Based on information from:
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt

import json
import os, struct, array
from fcntl import ioctl
from datetime import datetime
initStart=True
# These constants were borrowed from linux/input.h
class DriverJS(object):
	def __init__(self):
		self.axis_names = {
			0x00 : 'x',
			0x01 : 'y',
			0x02 : 'z',
			0x03 : 'rx',
			0x04 : 'ry',
			0x05 : 'rz',
			0x06 : 'throttle',
			0x07 : 'rudder',
			0x08 : 'wheel',
			0x09 : 'gas',
			0x0a : 'brake',
			0x10 : 'hat0x',
			0x11 : 'hat0y',
			0x12 : 'hat1x',
			0x13 : 'hat1y',
			0x14 : 'hat2x',
			0x15 : 'hat2y',
			0x16 : 'hat3x',
			0x17 : 'hat3y',
			0x18 : 'pressure',
			0x19 : 'distance',
			0x1a : 'tilt_x',
			0x1b : 'tilt_y',
			0x1c : 'tool_width',
			0x20 : 'volume',
			0x28 : 'misc',
		}

		self.button_names = {
			0x120 : 'trigger',
			0x121 : 'thumb',
			0x122 : 'thumb2',
			0x123 : 'top',
			0x124 : 'top2',
			0x125 : 'pinkie',
			0x126 : 'base',
			0x127 : 'base2',
			0x128 : 'base3',
			0x129 : 'base4',
			0x12a : 'base5',
			0x12b : 'base6',
			0x12f : 'dead',
			0x130 : 'a',
			0x131 : 'b',
			0x132 : 'c',
			0x133 : 'x',
			0x134 : 'y',
			0x135 : 'z',
			0x136 : 'tl',
			0x137 : 'tr',
			0x138 : 'tl2',
			0x139 : 'tr2',
			0x13a : 'select',
			0x13b : 'start',
			0x13c : 'mode',
			0x13d : 'thumbl',
			0x13e : 'thumbr',

			0x220 : 'dpad_up',
			0x221 : 'dpad_down',
			0x222 : 'dpad_left',
			0x223 : 'dpad_right',

			# XBox 360 controller uses these codes.
			0x2c0 : 'dpad_left',
			0x2c1 : 'dpad_right',
			0x2c2 : 'dpad_up',
			0x2c3 : 'dpad_down',
		}
		
		self.axis_states = {}
		self.button_states = {}
		self.axis_map = []
		self.button_map = []
		
		
		
	def LoopReadJS(self,init=False):
		if True:
			# Iterate over the joystick devices.
			if init: print('Available devices:')

			for fn in os.listdir('/dev/input'):
				if fn.startswith('js'):
					if init: print('  /dev/input/%s' % (fn))

			if init:
				# We'll store the states here.
				self.axis_states = {}
				self.button_states = {}

				self.axis_map = []
				self.button_map = []
				# Open the joystick device.
				self.fn = '/dev/input/js0'
				print('Opening %s...' % self.fn)
				self.jsdev = open(self.fn, 'rb')

				# Get the device name.
				#buf = bytearray(63)
				buf = array.array('B', [0] * 64)
				ioctl(self.jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
				js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8')
				print('Device name: %s' % js_name)

				# Get number of axes and buttons.
				buf = array.array('B', [0])
				ioctl(self.jsdev, 0x80016a11, buf) # JSIOCGAXES
				num_axes = buf[0]

				buf = array.array('B', [0])
				ioctl(self.jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
				num_buttons = buf[0]

				# Get the axis map.
				buf = array.array('B', [0] * 0x40)
				ioctl(self.jsdev, 0x80406a32, buf) # JSIOCGAXMAP

				for axis in buf[:num_axes]:
					self.axis_name = self.axis_names.get(axis, 'unknown(0x%02x)' % axis)
					self.axis_map.append(self.axis_name)
					self.axis_states[self.axis_name] = 0.0

				# Get the button map.
				buf = array.array('H', [0] * 200)
				ioctl(self.jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

				for btn in buf[:num_buttons]:
					self.btn_name = self.button_names.get(btn, 'unknown(0x%03x)' % btn)
					self.button_map.append(self.btn_name)
					self.button_states[self.btn_name] = 0

					print('%d axes found: %s' % (num_axes, ', '.join(self.axis_map)))
					print('%d buttons found: %s' % (num_buttons, ', '.join(self.button_map)))
				
		
			evbuf = self.jsdev.read(8)
			#self.jsdev.close()
			if evbuf:
				time, value, type, number = struct.unpack('IhBB', evbuf)

				if type & 0x80:
					print("(initial)", end="")

				if type & 0x01:
					button = self.button_map[number]
					if button:
						self.button_states[button] = value
						if value:
							#jsdev.close()
							print("%s pressed" % (button))
							keyv="%s pressed" % (button)
							return {keyv:"pressed"}
						else:
							#jsdev.close()
							print("%s released" % (button))
							keyv="%s released" % (button)
							return {keyv:"released"}

				if type & 0x02:
					axis = self.axis_map[number]
					if axis:
						#jsdev.close()
						fvalue = value / 32767.0
						self.axis_states[axis] = fvalue
						print("%s: %.3f" % (axis, fvalue))
						return {axis: "%.3f" % (fvalue)}
				

def formatageFn(BUFFER0):
	Header = []
	Body = []
	for i in range(0,len(BUFFER0)):
		print("<<<",BUFFER0[i])
		for k,v in BUFFER0[i].items():
			BUFFER0[i] = {
				"key_name": k,
				"state": v
			}
		now = datetime.now()
		BUFFER0[i]["timestamp"] = now.strftime("%d/%m/%Y-%H:%M:%S")
		"""
		k,v = BUFFER0[i]
		if "pressed" in v:
			A = datetime.now()
		elif "released" in v:
			B = datetime.now()
			TIMEDELTA = B - A
			DELTA = TIMEDELTA.strftime("%d/%m/%Y-%H:%M:%S")
			BUFFER0[i]["delta"] = DELTA
		"""
			
		if i <= 18:
			Header.append(BUFFER0[i])
		else:
			Body.append(BUFFER0[i])
	return Header, Body
			

djs = DriverJS()
BUFFER0=[]
# Main event loop
while True:
	ev2buf=djs.LoopReadJS(initStart)
	initStart=False
	print(ev2buf)
	BUFFER0.append(ev2buf)
	print("count --> {}".format(len(BUFFER0)))
	if len(BUFFER0) == 19 + 4*2: #19 init + 4*2 :4 pull down/up
		Header, Body = formatageFn(BUFFER0)
		with open("out.json",'wb') as f1:
			f1.write(json.dumps({"header":Header,"body":Body},sort_keys=True, indent=4).encode())
			f1.close()
			exit(0)
