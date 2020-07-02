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

	def modifyDamage(self, rawDamage, damageSchool):
		damage = rawDamage * self.damageModifiers[damageSchool]
		return damage

	def apply(self, effect, TS):
		existingEffect = next((e for e in self.effects if e.name == effect.name), None)
		if type(effect) is Debuff:
			if existingEffect is None:
				self.effects.append(effect)
				return effect
			else:
				existingEffect.refresh()
				return existingEffect
		elif type(effect) is DoT:
			
			effect.tickDamage = self.modifyDamage(rawTickDamage, effect.school)
			effect.lastTickTS = TS
			if existingEffect is None:
				self.effects.append(effect)
				return effect
			else:
				if effect.maxStacks > 1:
					existingEffect.refresh(effect.tickDamage)
					return existingEffect
				else:
					self.effects.remove(existingEffect)
					self.effects.append(effect)
					return effect

			self.effects.append(effect)
			return effect

	def updateModifiers(self, elapsedTime):
		for sch in self.damageModifiers:
			self.damageModifiers[sch] = math.prod([math.pow(e.schoolDamageMultiplier, e.currentStack)  for e in self.effects if type(e) is Debuff and e.school == sch])
		return self.damageModifiers

# TODO make damage class. target.damageTaken wil be a list of damage, to make analysis at the end easier