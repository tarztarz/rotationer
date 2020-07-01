from spell_classes import *
import random
from enum import Enum
import copy
import math

class CasterState(Enum):
	IDLE = 0
	CASTING = 1

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
	
	def __repr__(self):
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
		effects = [copy.deepcopy(x) for x in spell.effects]
		onCritEffects = [copy.deepcopy(x) for x in spell.onCritEffects]
		effects = effects + onCritEffects if isCrit else effects

		projectile = Projectile(caster=self, target=self.target, spell=spell, travelTime=spell.travelTime, damage=finalSpellDamage, school=spell.school, effects=effects, isCrit=isCrit)
		return projectile
	
	def updateState(self, elapsedTime):
		if self.state == CasterState.CASTING:
			self.channelingElapsed += elapsedTime

		if self.channelingSpell is not None and self.channelingElapsed >= self.channelingSpell.castTime:
			projectile = self.finishCast()
			self.channelingElapsed = 0
			self.target = None
			self.channelingSpell = None
			self.state = CasterState.IDLE
			return projectile

		return None
 
class Target:
	def __init__(self, name):
		self.name = name
		self.damageTaken = 0
		self.landedProjectiles = []
		self.effects = []
		self.damageModifiers = {school: 1.0 for school in SpellSchool}

	def deal(self, rawDamage, damageSchool):
		damage = rawDamage * self.damageModifiers[damageSchool]
		self.damageTaken += damage
		return damage

	def apply(self, effect):
		if type(effect) is Debuff:
			previousDebuff = next((e for e in self.effects if e.name == effect.name), None)
			if previousDebuff is None:
				self.effects.append(effect)
				return effect
			else:
				previousDebuff.refresh()
				return previousDebuff
		else:
			self.effects.append(effect)
			return effect

	def updateModifiers(self, elapsedTime):
		for sch, mod in self.damageModifiers.items():
			mod = math.prod([e.schoolDamageMultiplier for e in self.effects if type(e) is Debuff and e.school == sch])
		return self.damageModifiers
