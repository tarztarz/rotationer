from enum import Enum
import logging

class Events(Enum):
	CASTSTART = 0
	CASTEND = 1
	PROJECTILELAND = 2
	PROJECTILEDAMAGE = 3
	DOTAPPLIED = 4
	DOTREFRESHED = 5
	DOTDAMAGE = 6
	DOTCLIPPED = 7
	DEBUFFAPPLIED = 8
	DEBUFFREFRESHED = 9

def setupLogging():
	logging.basicConfig(filename='log.log',level=logging.INFO, format='%(asctime)s %(message)s')

def logCastStart(TS, caster):
	logging.info('{0}: {1} started casting {2} at {3}. CastTime: {4}s'.format(TS,
		caster.name, caster.channelingSpell.name, caster.target.name, caster.channelingSpell.castTime))

def logCastEnd(TS, projectile):
	logging.info('{0}: {1} finished casting {2} at {3}. TravelTime: {4}s'.format(TS,
		projectile.caster.name, projectile.spell.name, projectile.target.name, projectile.spell.travelTime))

def logProjectileLand(TS, projectile):
	logging.info('{0}: {1} from {2} landed on {3} for {4} raw damage {5}'.format(TS,
		projectile.spell.name, projectile.caster.name, projectile.target.name, projectile.damage, 'CRITICAL' if projectile.isCrit else ''))

def logProjectileDamage(TS, projectile, damage):
	logging.info('{0}: {1} dealt {2} damage from {3} (projectile) cast by {4} after {5} modifier for {6}'.format(TS,
		projectile.target.name, damage, projectile.spell.name, projectile.caster.name, projectile.target.damageModifiers[projectile.school], projectile.school.name))

def logDotApplied(TS, dot, target):
	logging.info('{0}: {1} (dot) applied to {2} by {3} for {4} tick damage every {5}s for {6}s (stack size {7})'.format(TS,
		dot.name, target.name, dot.casterOwner.name, dot.tickDamage, dot.tick, dot.duration, dot.currentStack))

def logDotClipped(TS, dot, clippedDot, target):
	logging.info('{0}: {1} (dot) clipped at {2} by {3} (clipped time {8}s) for {4} tick damage every {5}s for {6}s (stack size {7})'.format(TS,
		dot.name, target.name, dot.casterOwner.name, dot.tickDamage, dot.tick, dot.duration, dot.currentStack, (clippedDot.duration - clippedDot.totalElapsedTime)))

def logDotRefreshed(TS, dot, refresherDot, target):
	logging.info('{0}: {1} (dot) on {2} owned by {3} refreshed by {4} (stack size {5}) for {6} tick damage every {7}s'.format(TS,
		dot.name, target.name, dot.casterOwner.name, refresherDot.casterOwner.name, dot.currentStack, dot.tickDamage, dot.tick))

def logDotDamage(TS, dot, target, damage, tickCount):
	logging.info('{0}: {1} dealt {2} damage from {3} (dot) owned by {4} (stack size {5}) from {6} ticks (last tick TS {7}s) (total uptime {8}s)'.format(TS,
		target.name, damage, dot.name, dot.casterOwner.name, dot.currentStack, tickCount, dot.lastTickTS, dot.uptime))

def logDebuffApplied(TS, debuff, target):
	logging.info('{0}: {1} (debuff) applied to {2} by {3} (stack size {4})'.format(TS,
		debuff.name, target.name, debuff.casterOwner.name, debuff.currentStack))

def logDebuffRefreshed(TS, debuff, refresherDebuff, target):
	logging.info('{0}: {1} (debuff) on {2} owned by {3} refreshed by {4} (stack size {5}) (total uptime {6}s)'.format(TS,
		debuff.name, target.name, debuff.casterOwner.name, refresherDebuff.casterOwner.name, debuff.currentStack, debuff.uptime))

log = {Events.CASTSTART: logCastStart,
	Events.CASTEND: logCastEnd,
	Events.PROJECTILELAND: logProjectileLand,
	Events.PROJECTILEDAMAGE: logProjectileDamage,
	Events.DOTAPPLIED: logDotApplied,
	Events.DOTREFRESHED: logDotRefreshed,
	Events.DOTDAMAGE: logDotDamage,
	Events.DEBUFFAPPLIED: logDebuffApplied,
	Events.DEBUFFREFRESHED: logDebuffRefreshed}