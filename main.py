from classes import *
from spell_classes import *
from log_helper import *
from enum import Enum

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
	c1.spells['scorch'].onCritEffects.append(Debuff(name='improved scorch', duration=30, caster=c1, school=SpellSchool.FIRE, maxStacks=5, schoolDamageMultiplier=1.03))
	c2 = Caster('Luri')
	c2.spells['scorch'] = Spell(name='scorch', castTime=1.5, travelTime=0, minDamage=237, maxDamage=280, powerCoefficient=0.429, critDamageMultiplier=2, school=SpellSchool.FIRE)
	c2.spells['scorch'].onCritEffects.append(Debuff(name='improved scorch', duration=30, caster=c2, school=SpellSchool.FIRE, maxStacks=5, schoolDamageMultiplier=1.03))
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
			log(Events.HIT, newTS, p.target.name, p.spell.name, p.caster.name, p.damage, 'CRITICAL' if p.isCrit else '')
		else:
			flyingProjectiles.append(p)
	return flyingProjectiles

def updateTarget(target, elapsedTime, newTS):
	target.updateModifiers(elapsedTime)

	for e in target.effects:
		e.totalElapsedTime += elapsedTime
		if type(e) is DoT:
			tickDamage = sum([e.tickDict[ts] for ts in e.tickDict if ts <= e.totalElapsedTime and ts > e.totalElapsedTime - elapsedTime])
			dmg = target.deal(tickDamage, e.school)
			log(Events.DAMAGE, newTS, target.name, dmg, e.name, e.caster.name, target.damageModifiers[p.school], e.school.name)
	target.effects = [e for e in target.effects if e.totalElapsedTime < e.duration]

	for p in target.landedProjectiles:
		dmg = target.deal(p.damage, p.school)
		log(Events.DAMAGE, newTS, p.target.name, p.damage, p.spell.name, p.caster.name, target.damageModifiers[p.school], p.school.name)
		for e in p.effects:
			modifiedEffect = target.apply(e)
			if type(modifiedEffect) is Debuff:
				log(Events.DEBUFFAPPLIED, newTS, modifiedEffect.name, target.name, modifiedEffect.caster.name, modifiedEffect.currentStack)
			elif type(e) is DoT:
				pass #log dot
	target.landedProjectiles = []

	return target

main()