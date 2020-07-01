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

		projectile = Projectile(caster=self, target=self.target, spell=spell, travelTime=spell.travelTime, damage=finalSpellDamage, school=spell.school, effects=effects, onCritEffects=onCritEffects, isCrit=isCrit)
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
		# apply modifiers then deal the damage
		damage = rawDamage * self.damageModifiers[damageSchool]
		self.damageTaken += damage

	def apply(self, effects):
		for e in effects:
			self.effects.append(e)

	def updateState(self, elapsedTime):
		for sch, mod in self.damageModifiers.items():
			mod = math.prod([e.schoolDamageMultiplier for e in self.effects if type(e) is Debuff and e.school == sch])

		for p in self.landedProjectiles:
			self.deal(p.damage, p.school)
			self.apply(p.effects)
		self.landedProjectiles = []

		for e in self.effects:
			e.totalElapsedTime += elapsedTime

			if type(e) is DoT:
				tickDamage = sum([e.tickDict[ts] for ts in e.tickDict if ts <= e.totalElapsedTime and ts > e.totalElapsedTime - elapsedTime])
				self.deal(tickDamage, e.school)
		self.effects = [e for e in self.effects if e.totalElapsedTime < e.duration]
