import random
from enum import Enum
import logging

class CasterState(Enum):
	IDLE = 0
	CASTING = 1

class SpellState(Enum):
	AVAILABLE = 0
	UNAVAILABLE = 1

class ProjectileState(Enum):
	FLYING = 0
	LANDED = 1

class Caster:
	def __init__(self, name):
		self.name = name
		self.power = 1
		self.hitChance = 1
		self.critChance = 0.3
		self.state = CasterState.IDLE
		self.channelingSpell = None
		self.channelingElapsed = 0
		self.spells = {}
		self.target = None
	
	def __str__(self):
		return 'CASTER: (name: {}, state: {})'.format(self.name, self.state)
	
	def startCast(self, spell, target):
		self.state = CasterState.CASTING
		self.channelingSpell = spell
		self.target = target

	def finishCast(self): #maybe have the spell calculate its own damage
		spell = self.channelingSpell
		rawSpellDamage = (spell.maxDamage - spell.minDamage) * random.random() + spell.minDamage
		modifiedSpellDamage = rawSpellDamage * self.power + spell.powerCoefficient
		isCrit = True if random.random() < self.critChance else False
		finalSpellDamage = modifiedSpellDamage * spell.critDamageMultiplier if isCrit else modifiedSpellDamage

		projectile = Projectile(source=self, target=self.target, spell=spell, travelTime=spell.travelTime, damage=finalSpellDamage, effect=None)
		self.target = None
		return projectile
	
	def updateState(self, elapsedTime):
		if self.state == CasterState.CASTING:
			self.channelingElapsed += elapsedTime

		if self.channelingSpell is not None and self.channelingElapsed >= self.channelingSpell.castTime:
			projectile = self.finishCast()
			self.state = CasterState.IDLE
			return projectile

		return None
    
class Spell:
	def __init__(self, name, castTime, travelTime, minDamage, maxDamage, powerCoefficient, effect, critDamageMultiplier):
		self.name = name
		self.castTime = castTime
		self.travelTime = travelTime
		self.minDamage = minDamage
		self.maxDamage = maxDamage
		self.effect = effect
		self.powerCoefficient = powerCoefficient
		self.critDamageMultiplier = critDamageMultiplier
		self.state = SpellState.AVAILABLE

class Projectile:
	def __init__(self, source, target, spell, travelTime, damage, effect):
		self.source = source
		self.target = target
		self.spell = spell
		self.travelTime = travelTime
		self.damage = damage
		self.effect = effect
		self.travelElapsed = 0
		self.state = ProjectileState.FLYING if self.travelTime >= self.travelElapsed else ProjectileState.LANDED

	def __str__(self):
		return 'PROJECTILE: (source: {}, target: {}, travelTime: {}, elapsed: {}, state: {})'.format(self.source.name,
			self.target.name, self.travelTime, self.travelElapsed, self.state)

	def land(self):
		self.target.deal(self.damage)
		self.target.apply(self.effect)
		self.state = ProjectileState.LANDED

	def updateState(self, elapsedTime):
		if self.state == ProjectileState.FLYING:
			self.travelElapsed += elapsedTime
		
		if self.travelElapsed >= self.travelTime:
			self.state = ProjectileState.LANDED

class Target:
	def __init__(self, name):
		self.name = name
		self.damageTaken = 0
		self.landedProjectiles = []

	def deal(self, damage):
		self.damageTaken += damage

	def apply(self, effect):
		pass

	def updateState(self, elapsedTime):
		for p in self.landedProjectiles:
			self.deal(p.damage)
			self.apply(p.effect)
		self.landedProjectiles = []