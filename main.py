from classes import *
from spell_classes import *
from enum import Enum
import logging

CASTERS = 'casters'
PROJECTILES = 'projectiles'
TARGET = 'target'
TS = 'ts'

class Events(Enum):
	CASTSTART = 0
	CASTEND = 1
	HIT = 2

def main():
	logging.basicConfig(filename='log.log',level=logging.INFO, format='%(asctime)s %(message)s')
	stateHistory = [initializeState()]

	step = 1
	for i in range(step, 100, step):
		stateHistory.append(updateState(stateHistory[-1], step/2.0))

	logging.info('end: {} took {} total damage'.format(stateHistory[-1][TARGET].name, stateHistory[-1][TARGET].damageTaken))

def initializeState():
	c1 = Caster('Tarz')
	c1.spells['scorch'] = Spell(name='scorch', castTime=1.5, travelTime=0, minDamage=237, maxDamage=280, powerCoefficient=0.429, critDamageMultiplier=2, school=SpellSchool.FIRE)
	c1.spells['scorch'].onCritEffects.append(Debuff(duration=30, school=SpellSchool.FIRE, maxStacks=5, schoolDamageMultiplier=1.03))
	c2 = Caster('Luri')
	c2.spells['scorch'] = Spell(name='scorch', castTime=1.5, travelTime=0, minDamage=237, maxDamage=280, powerCoefficient=0.429, critDamageMultiplier=2, school=SpellSchool.FIRE)
	c2.spells['scorch'].onCritEffects.append(Debuff(duration=30, school=SpellSchool.FIRE, maxStacks=5, schoolDamageMultiplier=1.03))
	state = {CASTERS: [c1, c2],
		PROJECTILES: [],
		TARGET: Target('dummy'),
		TS: 0}
	logging.info('State initialized: {}'.format(state))
	return state

def updateState(previousState, elapsedTime):
	newTS = previousState[TS] + elapsedTime
	newState = {CASTERS: [],
		PROJECTILES: [],
		TARGET: None,
		TS: newTS}

	for c in previousState[CASTERS]:
		if c.state == CasterState.IDLE:
			c.startCast(spell=c.spells['scorch'], target=previousState[TARGET])
			log(Events.CASTSTART, newTS, c.name, c.channelingSpell.name, c.target.name, c.channelingSpell.castTime)
		else:
			p = c.updateState(elapsedTime)
			if p is not None:
				log(Events.CASTEND, newTS, p.caster.name, p.spell.name, p.target.name, p.spell.travelTime)
				if p.state == ProjectileState.LANDED:
					p.target.landedProjectiles.append(p)
					log(Events.HIT, newTS, p.target.name, p.damage, 'CRITICAL' if p.isCrit else '')
				else:
					newState[PROJECTILES].append(p)
		newState[CASTERS].append(c)

	for p in previousState[PROJECTILES]:
		p.updateState(elapsedTime)

		if p.state == ProjectileState.LANDED:
			p.target.landedProjectiles.append(p)
			log(Events.HIT, newTS, p.target.name, p.damage, 'CRITICAL' if p.isCrit else '')
		else:
			newState[PROJECTILES].append(p)

	t = previousState[TARGET]
	t.updateState(elapsedTime)
	newState[TARGET] = t
	
	return newState

def log(event, *args):
	if event == Events.CASTSTART:
		logging.info('{}: {} started casting {} at {}. CastTime: {}s'.format(*args))
	elif event == Events.CASTEND:
		logging.info('{}: {} finished casting {} at {}. TravelTime: {}s'.format(*args))
	elif event == Events.HIT:
		logging.info('{}: {} hit with {} damage {}'.format(*args))

main()