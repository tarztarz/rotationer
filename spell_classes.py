import random
from enum import Enum
import logging
import math

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
		for e in self.effects:
			e.casterOwner = self.caster
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
	def __init__(self, name, duration, maxStacks, school):
		self.name = name
		self.duration = duration
		self.maxStacks = maxStacks
		self.school = school
		self.totalElapsedTime = 0
		self.currentStack = 1
		self.casterOwner = None
		self.uptime = 0

class DoT(Effect):
	def __init__(self, name, duration, maxStacks, school, damageMultiplier, tick):
		super().__init__(name, duration, maxStacks, school)
		self.damageMultiplier = damageMultiplier
		self.tick = tick
		self.lastTickTS = 0
		self.tickDamage = 0

	def calculateTickDamage(self, projectileDamage):
		rawTotalDamage = self.damageMultiplier * projectileDamage
		maxTickCount = math.floor(self.duration / self.tick)
		return rawTotalDamage / maxTickCount

	def refresh(self, tickDamage):
		self.totalElapsedTime = 0
		if self.currentStack < self.maxStacks:
			self.currentStack += 1
			self.tickDamage += tickDamage
		else:
			self.currentStack = self.maxStacks

class Debuff(Effect):
	def __init__(self, name, duration, maxStacks, school, schoolDamageMultiplier):
		super().__init__(name, duration, maxStacks, school)
		self.schoolDamageMultiplier = schoolDamageMultiplier
	
	def refresh(self):
		self.totalElapsedTime = 0
		self.currentStack = self.currentStack + 1 if self.currentStack < self.maxStacks else self.maxStacks