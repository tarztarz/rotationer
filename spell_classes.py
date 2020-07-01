import random
from enum import Enum
import logging

class SpellState(Enum):
	AVAILABLE = 0
	UNAVAILABLE = 1

class ProjectileState(Enum):
	FLYING = 0
	LANDED = 1

class SpellSchool(Enum):
	FIRE = 0
	FROST = 1
	ARCANE = 2
   
class Spell:
	def __init__(self, name, castTime, travelTime, minDamage, maxDamage, powerCoefficient, critDamageMultiplier, school):
		self.name = name
		self.castTime = castTime
		self.travelTime = travelTime
		self.minDamage = minDamage
		self.maxDamage = maxDamage
		self.powerCoefficient = powerCoefficient
		self.critDamageMultiplier = critDamageMultiplier
		self.school = school
		self.effects = []
		self.onCritEffects = []
		self.state = SpellState.AVAILABLE

class Projectile:
	def __init__(self, caster, target, spell, travelTime, damage, school, effects, onCritEffects, isCrit=False):
		self.caster = caster
		self.target = target
		self.spell = spell
		self.travelTime = travelTime
		self.damage = damage
		self.school = school
		self.effects = effects
		self.onCritEffects = onCritEffects
		self.isCrit = isCrit
		self.travelElapsed = 0
		self.state = ProjectileState.FLYING if self.travelTime >= self.travelElapsed else ProjectileState.LANDED

	def __repr__(self):
		return 'PROJECTILE: (caster: {}, target: {}, travelTime: {}, elapsed: {}, state: {})'.format(self.caster.name,
			self.target.name, self.travelTime, self.travelElapsed, self.state)

	def land(self):
		self.target.deal(self.damage)
		self.target.apply(self.effect if not self.isCrit else self.effects + self.onCritEffects)
		self.state = ProjectileState.LANDED

	def updateState(self, elapsedTime):
		if self.state == ProjectileState.FLYING:
			self.travelElapsed += elapsedTime
		
		if self.travelElapsed >= self.travelTime:
			self.state = ProjectileState.LANDED

class Effect: #break this down
	def __init__(self, duration):
		self.duration = duration
		self.totalElapsedTime = 0

class DoT(Effect):
	def __init__(self, duration, totalDamage, ticks, school):
		super().__init__(duration)
		self.totalDamage = totalDamage
		self.ticks = ticks
		self.school = school
		self.tickDict = {}
		for ts in range(ticks):
			self.tickDict[ts] = self.totalDamage / ticks

class Debuff(Effect):
	def __init__(self, duration, school, maxStacks, schoolDamageMultiplier):
		super().__init__(duration)
		self.school = school
		self.maxStacks = maxStacks
		self.schoolDamageMultiplier = schoolDamageMultiplier