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
	def __init__(self, caster, target, spell, travelTime, damage, school, effects, isCrit=False):
		self.caster = caster
		self.target = target
		self.spell = spell
		self.travelTime = travelTime
		self.damage = damage
		self.school = school
		self.effects = effects
		self.isCrit = isCrit
		self.travelElapsed = 0
		self.state = ProjectileState.FLYING if self.travelTime >= self.travelElapsed else ProjectileState.LANDED

	def __repr__(self):
		return 'PROJECTILE: (caster: {}, target: {}, travelTime: {}, elapsed: {}, state: {})'.format(self.caster.name,
			self.target.name, self.travelTime, self.travelElapsed, self.state)

	def updateState(self, elapsedTime):
		if self.state == ProjectileState.FLYING:
			self.travelElapsed += elapsedTime
		
		if self.travelElapsed >= self.travelTime:
			self.state = ProjectileState.LANDED

class Effect: #break this down
	def __init__(self, name, duration, caster):
		self.name = name
		self.duration = duration
		self.caster = caster
		self.totalElapsedTime = 0

class DoT(Effect):
	def __init__(self, name, duration, caster, totalDamage, ticks, school):
		super().__init__(name, duration, caster)
		self.totalDamage = totalDamage
		self.ticks = ticks
		self.school = school
		self.tickDict = {}
		for ts in range(ticks):
			self.tickDict[ts] = self.totalDamage / ticks

class Debuff(Effect):
	def __init__(self, name, duration, caster, school, maxStacks, schoolDamageMultiplier):
		super().__init__(name, duration, caster)
		self.school = school
		self.maxStacks = maxStacks
		self.schoolDamageMultiplier = schoolDamageMultiplier
		self.currentStack = 1

	def refresh(self):
		self.totalElapsedTime = 0
		self.currentStack = self.currentStack + 1 if self.currentStack < self.maxStacks else self.maxStacks