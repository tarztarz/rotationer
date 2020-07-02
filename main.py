from classes import *
from spell_classes import *
from log_helper import *
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
			log(Events.CASTSTART, newTS, c.name, c.channelingSpell.name, c.target.name, c.channelingSpell.castTime)
		else:
			p = c.updateState(elapsedTime)
			if p is not None:
				log(Events.CASTEND, newTS, p.caster.name, p.spell.name, p.target.name, p.spell.travelTime)
				if p.state == ProjectileState.LANDED:
					p.target.landedProjectiles.append(p)
					log(Events.HIT, newTS, p.target.name, p.spell.name, p.caster.name, p.damage, 'CRITICAL' if p.isCrit else '')
				else:
					newProjectiles.append(p)
	return (casters, newProjectiles)

def updateProjectiles(projectiles, elapsedTime, newTS):
	flyingProjectiles = []
	for p in projectiles:
		p.updateState(elapsedTime)

		if p.state == ProjectileState.LANDED:
			p.target.landedProjectiles.append(p)
			log(Events.PROJECTILEHIT, newTS, p.target.name, p.spell.name, p.caster.name, p.damage, 'CRITICAL' if p.isCrit else '')
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
				log(Events.DOTDAMAGE, newTS, e.name, target.name, totalDamage, e.casterOwner, e.currentStack, tickCount, e.lastTickTS, e.uptime)
	target.effects = [e for e in target.effects if e.totalElapsedTime < e.duration]

	for p in target.landedProjectiles:
		dmg = target.modifyDamage(p.damage, p.school)
		target.damageTaken += dmg
		log(Events.PROJECTILEDAMAGE, newTS, target.name, dmg, p.spell.name, p.caster.name, target.damageModifiers[p.school], p.school.name)
		
		for deb in (e for e in p.effects if type(e) is Debuff):
			existingDebuff = next((e for e in target.effects if e.name == deb.name), None)
			if existingDebuff is None:
				target.effects.append(deb)
				log(Events.DEBUFFAPPLIED, newTS, deb.name, target.name, deb.casterOwner.name, deb.currentStack)
			else:
				existingDebuff.refresh()
				log(Events.DEBUFFREFRESHED, newTS, existingDebuff.name, target.name, deb.casterOwner.name, existingDebuff.casterOwner.name, existingDebuff.currentStack)
			
		for dot in (e for e in p.effects if type(e) is DoT):
			oldDot = next((e for e in target.effects if e.name == dot.name), None)
			dot.tickDamage = target.modifyDamage(dot.calculateTickDamage(p.damage), dot.school)
			dot.lastTickTS = newTS
			if oldDot is None:
				target.effects.append(dot)
				log(Events.DOTAPPLIED, newTS, dot.name, target.name, dot.casterOwner.name, dot.tickDamage, dot.tick, dot.duration, dot.currentStack)
			else:
				if oldDot.maxStacks > 1:
					oldDot.refresh(dot.tickDamage)
					log(Events.DOTREFRESHED, newTS, oldDot.name, target.name, oldDot.tickDamage, oldDot.casterOwner.name, dot.casterOwner.name, oldDot.currentStack, oldDot.uptime)
				else:
					target.effects.remove(oldDot)
					target.effects.append(dot)
					# TODO Events.DOTREPLACED
					log(Events.DOTAPPLIED, newTS, dot.name, target.name, dot.casterOwner.name, dot.tickDamage, dot.tick, dot.duration, dot.currentStack)			
	target.landedProjectiles = []
	return target

main()