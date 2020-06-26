from classes import *
from enum import Enum
import logging

CASTERS = 'casters'
PROJECTILES = 'projectiles'
TARGET = 'target'
TS = 'ts'

def main():
	logging.basicConfig(filename='log.log',level=logging.INFO, format='%(asctime)s %(message)s')
	stateHistory = [initializeState()]

	step = 1
	for i in range(step, 20, step):
		stateHistory.append(updateState(stateHistory[-1], step/2.0))

def initializeState():
	c1 = Caster('Tarz')
	c1.spells['scorch'] = Spell(name='scorch', castTime=1.5, travelTime=0, minDamage=237, maxDamage=280, powerCoefficient=0.429, effect=None, critDamageMultiplier=2)
	state = {CASTERS: [c1],
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
			logging.info('{}: {} started casting {} at {}. CastTime: {}'.format(newTS,
				c.name, c.channelingSpell.name, c.target.name, c.channelingSpell.castTime))
		else:
			p = c.updateState(elapsedTime)
			if p is not None:
				logging.info('{}: {} casted {} at {}. TravelTime: {}'.format(newTS,
					p.source.name, p.spell.name, p.target.name, p.spell.travelTime))
				if p.state == ProjectileState.LANDED:
					p.target.landedProjectiles.append(p)
					logging.info('{}: {} hit with {} damage'.format(newTS,
						p.target.name, p.damage))
				else:
					newState[PROJECTILES].append(p)
		newState[CASTERS].append(c)

	for p in previousState[PROJECTILES]:
		p.updateState(elapsedTime)

		if p.state == ProjectileState.LANDED:
			p.target.landedProjectiles.append(p)
			logging.info('{}: {} hit with {} damage'.format(newTS,
						p.target.name, p.damage))
		else:
			newState[PROJECTILES].append(p)

	t = previousState[TARGET]
	t.updateState(elapsedTime)
	logging.info('{}: {} took {} total damage'.format(newTS,
		t.name, t.damageTaken))
	newState[TARGET] = t
	
	return newState

main()