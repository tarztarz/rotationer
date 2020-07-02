from enum import Enum
import logging

class Events(Enum):
	CASTSTART = 0
	CASTEND = 1
	PROJECTILEHIT = 2
	PROJECTILEDAMAGE = 3
	DOTAPPLIED = 4
	DOTREFRESHED = 5
	DOTDAMAGE = 6
	DEBUFFAPPLIED = 7
	DEBUFFREFRESHED = 8

def setupLogging():
	logging.basicConfig(filename='log.log',level=logging.INFO, format='%(asctime)s %(message)s')

def log(event, *args): # TODO: log as dict of functions with defined parameters (no more *args bs)
	if event == Events.CASTSTART:
		logging.info('{}: {} STARTED CASTING {} at {}. CastTime: {}s'.format(*args))
	elif event == Events.CASTEND:
		logging.info('{}: {} FINISHED CASTING {} at {}. TravelTime: {}s'.format(*args))
	elif event == Events.PROJECTILEHIT:
		logging.info('{}: {} HIT with {} ({}), {} raw damage {}'.format(*args))
	elif event == Events.PROJECTILEDAMAGE:
		logging.info('{}: {} DEALT {} damage from {} ({}) after {} modifier for {}'.format(*args))
	elif event == Events.DOTAPPLIED:
		logging.info('{}: {} APPLIED to {} by {} for {} damage every {}s for {}s (stack size {})'.format(*args))
	elif event == Events.DOTREFRESHED:
		logging.info('{} DOT REFRESHED | dot: {}, target: {}, new tick damage: {}, refresher: {}, owner: {}, stack size: {}, uptime: {}s'.format(*args))
	elif event == Events.DOTDAMAGE:
		logging.info('{} DOT DAMAGE | dot: {}, target: {}, damage: {}, caster: {}, stack size: {}, ticks: {}, last tick TS: {}s, uptime: {}s'.format(*args))
	elif event == Events.DEBUFFAPPLIED:
		logging.info('{}: {} APPLIED to {} by {} (stack size {})'.format(*args))
	elif event == Events.DEBUFFREFRESHED:
		logging.info('{} DEBUFF REFRESHED | debuff: {}, target: {}, caster: {}, owner: {}, stack size: {}'.format(*args))