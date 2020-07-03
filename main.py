from classes import *
from spell_classes import *
from log_helper import logs, setupLogging, Events
from enum import Enum
import math

CASTERS = 'casters'
PROJECTILES = 'projectiles'
TARGET = 'target'
TS = 'ts'

def main():
	setupLogging()
	stateHistory = [initializeState()]

	step = 1
	for i in range(step, 100, step):
		stateHistory.append(updateState(stateHistory[-1], step/2.0))

	logging.info('end: {} took {} total damage'.format(stateHistory[-1][TARGET].name, stateHistory[-1][TARGET].damageTaken))

def initializeState():
	# TODO spell and effects library
	# TODO rotations
	c1 = Caster('Tarz')
	c1.spells['scorch'] = Spell(name='scorch', castTime=1.5, travelTime=0, minDamage=237, maxDamage=280, powerCoefficient=0.429, critDamageMultiplier=2, school=SpellSchool.FIRE)
	c1.spells['scorch'].onCritEffects.append(Debuff(name='improved scorch', duration=30, maxStacks=5, school=SpellSchool.FIRE, schoolDamageMultiplier=1.03))
	c1.spells['scorch'].onCritEffects.append(DoT(name='ignite', duration=4, maxStacks=5, school=SpellSchool.FIRE, damageMultiplier=0.4, tick=1))
	c2 = Caster('Luri')
	c2.spells['scorch'] = Spell(name='scorch', castTime=1.5, travelTime=0, minDamage=237, maxDamage=280, powerCoefficient=0.429, critDamageMultiplier=2, school=SpellSchool.FIRE)
	c2.spells['scorch'].onCritEffects.append(Debuff(name='improved scorch', duration=30, maxStacks=5, school=SpellSchool.FIRE, schoolDamageMultiplier=1.03))
	state = {CASTERS: [c1, c2],
		PROJECTILES: [],
		TARGET: Target('dummy'),
		TS: 0}
	logging.info('State initialized: {}'.format(state))
	return state

def updateState(previousState, elapsedTime):
	newTS = previousState[TS] + elapsedTime
	newState = {CASTERS: None,
		PROJECTILES: None,
		TARGET: None,
		TS: newTS}

	newState[CASTERS], newState[PROJECTILES] = updateCasters(casters=previousState[CASTERS], target=previousState[TARGET], elapsedTime=elapsedTime, newTS=newTS)
	newState[PROJECTILES] += updateProjectiles(projectiles=previousState[PROJECTILES], elapsedTime=elapsedTime, newTS=newTS)
	newState[TARGET] = updateTarget(target=previousState[TARGET], elapsedTime=elapsedTime, newTS=newTS)
	
	return newState

def updateCasters(casters, target, elapsedTime, newTS):
	newProjectiles = []
	for c in casters:
		if c.state == CasterState.IDLE:
			c.startCast(spell=c.spells['scorch'], target=target)
			logs[Events.CASTSTART](TS=newTS, caster=c)
		else:
			p = c.updateState(elapsedTime)
			if p is not None:
				logs[Events.CASTEND](TS=newTS, projectile=p)
				if p.state == ProjectileState.LANDED:
					p.target.landedProjectiles.append(p)
					logs[Events.PROJECTILELAND](TS=newTS, projectile=p)
				else:
					newProjectiles.append(p)
	return (casters, newProjectiles)

def updateProjectiles(projectiles, elapsedTime, newTS):
	flyingProjectiles = []
	for p in projectiles:
		p.updateState(elapsedTime)

		if p.state == ProjectileState.LANDED:
			p.target.landedProjectiles.append(p)
			logs[Events.PROJECTILELAND](TS=newTS, projectile=p)
		else:
			flyingProjectiles.append(p)
	return flyingProjectiles

def updateTarget(target, elapsedTime, newTS):
	target.updateModifiers(elapsedTime)

	for e in target.effects:
		e.totalElapsedTime += elapsedTime
		if type(e) is DoT:
			tickCount = math.floor((newTS - e.lastTickTS) / e.tick)
			if tickCount > 0:
				totalDamage = e.tickDamage * tickCount
				target.damageTaken += totalDamage
				e.lastTickTS = e.lastTickTS + (tickCount * e.tick)
				e.uptime += (tickCount * e.tick)
				logs[Events.DOTDAMAGE](TS=newTS, dot=e, target=target, damage=totalDamage, tickCount=tickCount)
		elif type(e) is Debuff:
			e.uptime += newTS
	target.effects = [e for e in target.effects if e.totalElapsedTime < e.duration]

	for p in target.landedProjectiles:
		dmg = target.modifyDamage(p.damage, p.school)
		target.damageTaken += dmg
		logs[Events.PROJECTILEDAMAGE](TS=newTS, projectile=p, damage=dmg)
		
		for deb in (e for e in p.effects if type(e) is Debuff):
			existingDebuff = next((e for e in target.effects if e.name == deb.name), None)
			if existingDebuff is None:
				target.effects.append(deb)
				logs[Events.DEBUFFAPPLIED](TS=newTS, debuff=deb, target=target)
			else:
				existingDebuff.refresh()
				logs[Events.DEBUFFREFRESHED](TS=newTS, debuff=existingDebuff, refresherDebuff=deb, target=target)
			
		for dot in (e for e in p.effects if type(e) is DoT):
			oldDot = next((e for e in target.effects if e.name == dot.name), None)
			dot.tickDamage = target.modifyDamage(dot.calculateTickDamage(p.damage), dot.school)
			dot.lastTickTS = newTS
			if oldDot is None:
				target.effects.append(dot)
				logs[Events.DOTAPPLIED](TS=newTS, dot=dot, target=target)
			else:
				if oldDot.maxStacks > 1:
					oldDot.refresh(dot.tickDamage)
					logs[Events.DOTREFRESHED](TS=newTS, dot=oldDot, refresherDot=dot, target=target)
				else:
					target.effects.remove(oldDot)
					target.effects.append(dot)
					logs[Events.DOTCLIPPED](TS=newTS, dot=dot, clippedDot=oldDot, target=target)
	target.landedProjectiles = []
	return target

main()